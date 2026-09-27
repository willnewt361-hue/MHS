"""
Payment & Subscription Service Module
Handles subscriptions, payments (MTN/Airtel), invoices, and monetization
"""

import json
import uuid
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
import requests

class PaymentService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.mtn_api_url = os.getenv('MTN_API_URL', 'https://api.mtn.com')
        self.mtn_api_key = os.getenv('MTN_API_KEY')
        self.airtel_api_url = os.getenv('AIRTEL_API_URL', 'https://api.airtel.com')
        self.airtel_api_key = os.getenv('AIRTEL_API_KEY')
        
    def create_subscription_plan(self, plan_name, plan_type, price, billing_cycle, 
                                features, max_users=-1, description=""):
        """Create subscription plan"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            features_json = json.dumps(features) if isinstance(features, list) else features
            
            cur.execute("""
                INSERT INTO subscription_plans 
                (plan_name, plan_type, price, billing_cycle, currency, description, 
                 features, max_users, is_active)
                VALUES (%s, %s, %s, %s, 'USD', %s, %s, %s, 1)
                RETURNING id
            """, (plan_name, plan_type, price, billing_cycle, description, 
                  features_json, max_users))
            
            plan_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'plan_id': plan_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def subscribe_user(self, user_id, plan_id, auto_renew=True):
        """Subscribe user to a plan"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get plan duration
            cur.execute("""
                SELECT billing_cycle, price FROM subscription_plans WHERE id = %s
            """, (plan_id,))
            
            plan = cur.fetchone()
            if not plan:
                return {'success': False, 'error': 'Plan not found'}
            
            # Calculate dates
            start_date = datetime.now()
            if plan['billing_cycle'] == 'monthly':
                end_date = start_date + timedelta(days=30)
            else:  # yearly
                end_date = start_date + timedelta(days=365)
            
            auto_renew_date = end_date if auto_renew else None
            
            # Check if user already has active subscription
            cur.execute("""
                SELECT id FROM user_subscriptions 
                WHERE user_id = %s AND subscription_status = 'active'
            """, (user_id,))
            
            existing = cur.fetchone()
            if existing:
                # Cancel existing subscription
                cur.execute("""
                    UPDATE user_subscriptions 
                    SET subscription_status = 'cancelled'
                    WHERE id = %s
                """, (existing['id'],))
            
            # Create new subscription
            cur.execute("""
                INSERT INTO user_subscriptions 
                (user_id, plan_id, subscription_status, start_date, end_date, 
                 auto_renew, auto_renew_date)
                VALUES (%s, %s, 'active', %s, %s, %s, %s)
                RETURNING id
            """, (user_id, plan_id, start_date, end_date, 1 if auto_renew else 0, 
                  auto_renew_date))
            
            subscription_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'subscription_id': subscription_id, 'price': plan['price']}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def initiate_mtn_payment(self, user_id, phone_number, amount, subscription_id=None):
        """Initiate MTN Mobile Money payment"""
        try:
            transaction_id = str(uuid.uuid4())
            
            # Call MTN API
            headers = {'Authorization': f'Bearer {self.mtn_api_key}'}
            payload = {
                'amount': amount,
                'currency': 'UGX',
                'externalId': transaction_id,
                'payer': {'partyIdType': 'MSISDN', 'partyId': phone_number},
                'payerMessage': 'Mengo-Hub Premium Subscription',
                'payeeNote': 'Subscription Payment'
            }
            
            response = requests.post(
                f'{self.mtn_api_url}/collection/v1_0/requesttopay',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 202:
                return {'success': False, 'error': f'MTN API error: {response.text}'}
            
            mtn_request_id = response.headers.get('X-Reference-Id')
            
            # Record transaction
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO mtn_payments 
                (transaction_id, user_id, phone_number, amount, status, mtn_request_id)
                VALUES (%s, %s, %s, %s, 'pending', %s)
            """, (transaction_id, user_id, phone_number, amount, mtn_request_id))
            
            # Record in main payment table
            cur.execute("""
                INSERT INTO payment_transactions 
                (user_id, subscription_id, amount, currency, payment_method, 
                 transaction_id, external_reference, status)
                VALUES (%s, %s, %s, 'USD', 'mtn', %s, %s, 'pending')
            """, (user_id, subscription_id, amount, transaction_id, mtn_request_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'transaction_id': transaction_id, 'mtn_request_id': mtn_request_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def initiate_airtel_payment(self, user_id, phone_number, amount, subscription_id=None):
        """Initiate Airtel Money payment"""
        try:
            transaction_id = str(uuid.uuid4())
            
            # Call Airtel API
            headers = {'Authorization': f'Bearer {self.airtel_api_key}'}
            payload = {
                'reference': transaction_id,
                'subscriber': {'phone': phone_number},
                'transaction': {
                    'amount': amount,
                    'currency': 'UGX',
                    'id': transaction_id
                },
                'merchant': {'name': 'Mengo-Hub'}
            }
            
            response = requests.post(
                f'{self.airtel_api_url}/merchant/v2/payments',
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Airtel API error: {response.text}'}
            
            result = response.json()
            airtel_request_id = result.get('data', {}).get('id')
            
            # Record transaction
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO airtel_payments 
                (transaction_id, user_id, phone_number, amount, status, airtel_request_id)
                VALUES (%s, %s, %s, %s, 'pending', %s)
            """, (transaction_id, user_id, phone_number, amount, airtel_request_id))
            
            # Record in main payment table
            cur.execute("""
                INSERT INTO payment_transactions 
                (user_id, subscription_id, amount, currency, payment_method, 
                 transaction_id, external_reference, status)
                VALUES (%s, %s, %s, 'USD', 'airtel', %s, %s, 'pending')
            """, (user_id, subscription_id, amount, transaction_id, airtel_request_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'transaction_id': transaction_id, 'airtel_request_id': airtel_request_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def confirm_payment(self, transaction_id, payment_method):
        """Confirm payment completed"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if payment_method == 'mtn':
                # Check MTN payment status
                cur.execute("""
                    SELECT user_id, amount FROM mtn_payments 
                    WHERE transaction_id = %s
                """, (transaction_id,))
            else:  # airtel
                cur.execute("""
                    SELECT user_id, amount FROM airtel_payments 
                    WHERE transaction_id = %s
                """, (transaction_id,))
            
            payment = cur.fetchone()
            if not payment:
                return {'success': False, 'error': 'Payment not found'}
            
            # Update transaction status
            cur.execute("""
                UPDATE payment_transactions 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE transaction_id = %s
            """, (transaction_id,))
            
            if payment_method == 'mtn':
                cur.execute("""
                    UPDATE mtn_payments SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE transaction_id = %s
                """, (transaction_id,))
            else:
                cur.execute("""
                    UPDATE airtel_payments SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE transaction_id = %s
                """, (transaction_id,))
            
            # Update user subscription if exists
            cur.execute("""
                SELECT subscription_id FROM payment_transactions 
                WHERE transaction_id = %s
            """, (transaction_id,))
            
            sub_row = cur.fetchone()
            if sub_row and sub_row['subscription_id']:
                cur.execute("""
                    UPDATE user_subscriptions 
                    SET subscription_status = 'active'
                    WHERE id = %s
                """, (sub_row['subscription_id'],))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'user_id': payment['user_id']}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def generate_invoice(self, user_id, transaction_id, amount, description=""):
        """Generate invoice"""
        try:
            import uuid
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
            
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO invoices 
                (invoice_number, user_id, transaction_id, amount, currency, 
                 invoice_date, due_date, status)
                VALUES (%s, %s, %s, %s, 'USD', CURRENT_DATE, 
                        CURRENT_DATE + INTERVAL '30 days', 'paid')
            """, (invoice_number, user_id, transaction_id, amount))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'invoice_number': invoice_number}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_subscription(self, user_id):
        """Get user's active subscription"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT us.id, us.subscription_status, us.start_date, us.end_date,
                    sp.plan_name, sp.plan_type, sp.price, sp.features
                FROM user_subscriptions us
                JOIN subscription_plans sp ON us.plan_id = sp.id
                WHERE us.user_id = %s AND us.subscription_status = 'active'
                ORDER BY us.start_date DESC
                LIMIT 1
            """, (user_id,))
            
            sub = cur.fetchone()
            cur.close()
            
            if sub:
                sub_dict = dict(sub)
                if sub_dict.get('features'):
                    sub_dict['features'] = json.loads(sub_dict['features'])
                return {'success': True, 'subscription': sub_dict}
            
            return {'success': True, 'subscription': None}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_payment_history(self, user_id):
        """Get user's payment history"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, amount, currency, payment_method, status, 
                    created_at, completed_at
                FROM payment_transactions
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            payments = cur.fetchall()
            cur.close()
            
            return {'success': True, 'payments': [dict(p) for p in payments]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cancel_subscription(self, user_id):
        """Cancel user's subscription"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE user_subscriptions 
                SET subscription_status = 'cancelled'
                WHERE user_id = %s AND subscription_status = 'active'
            """, (user_id,))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}

# Initialize service
payment_service = None

def init_payment_service(db_connection):
    global payment_service
    payment_service = PaymentService(db_connection)
    return payment_service
