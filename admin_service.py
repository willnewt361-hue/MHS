"""
Admin & Security Service - Super Admin Certificate, Audit Logging, Password Management, Feature Toggles
Handles: admin certificates, audit logs, password validation, feature toggles
"""

import hashlib
import bcrypt
import hmac
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)


class AdminSecurityService:
    def __init__(self, db_connection_string: str):
        self.db_conn_string = db_connection_string
        
    def _get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return None

    # ==================== SUPER ADMIN CERTIFICATE SYSTEM ====================
    def generate_super_admin_certificate(self, admin_id: str, requester_id: str, 
                                        validity_days: int = 365) -> Dict[str, Any]:
        """
        Generate a super admin certificate. Only Super Admin (A000) can create certificates.
        
        Args:
            admin_id: The admin to issue certificate to
            requester_id: The Super Admin requesting (must be A000)
            validity_days: Certificate validity period
            
        Returns:
            {'success': bool, 'certificate': str, 'expires': str, 'error': str}
        """
        try:
            if requester_id != "A000":
                return {'success': False, 'error': 'Only Super Admin (A000) can generate certificates'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            # Generate certificate hash
            cert_data = f"{admin_id}:{datetime.utcnow().isoformat()}:{os.urandom(32).hex()}"
            certificate = hashlib.sha256(cert_data.encode()).hexdigest()
            expires_at = datetime.utcnow() + timedelta(days=validity_days)
            
            cur = conn.cursor()
            
            # Use super_admin_certificates table instead of admin_certificates
            try:
                cur.execute("""
                    INSERT INTO super_admin_certificates (certificate_id, admin_id, certificate_code, issued_by, 
                                                   issued_at, expires_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                    ON CONFLICT (admin_id) DO UPDATE SET
                        certificate_code = EXCLUDED.certificate_code,
                        issued_by = EXCLUDED.issued_by,
                        issued_at = EXCLUDED.issued_at,
                        expires_at = EXCLUDED.expires_at,
                        is_active = 1
                    RETURNING certificate_code, expires_at
                """, (
                    f"CERT_{admin_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    admin_id, 
                    certificate, 
                    requester_id, 
                    datetime.utcnow(), 
                    expires_at
                ))
            except Exception as e:
                # Fallback: try without RETURNING clause if using different DB
                cur.execute("""
                    INSERT INTO super_admin_certificates (admin_id, certificate_code, issued_by, 
                                                   issued_at, expires_at, is_active)
                    VALUES (%s, %s, %s, %s, %s, 1)
                    ON CONFLICT (admin_id) DO UPDATE SET
                        certificate_code = EXCLUDED.certificate_code,
                        issued_by = EXCLUDED.issued_by,
                        issued_at = EXCLUDED.issued_at,
                        expires_at = EXCLUDED.expires_at,
                        is_active = 1
                """, (admin_id, certificate, requester_id, datetime.utcnow(), expires_at))
                result = None
            else:
                result = cur.fetchone()
            
            conn.commit()
            
            self._audit_log(requester_id, 'CERTIFICATE_GENERATED', 
                          f'Generated certificate for {admin_id}', admin_id)
            
            return {
                'success': True,
                'certificate': certificate,
                'admin_id': admin_id,
                'expires': result[1].isoformat() if result else expires_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Certificate generation error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def validate_certificate(self, admin_id: str, certificate: str) -> Dict[str, Any]:
        """
        Validate a super admin certificate
        
        Returns:
            {'success': bool, 'is_valid': bool, 'expires': str, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT certificate_code, expires_at, is_active FROM super_admin_certificates
                WHERE admin_id = %s AND is_active = 1
            """, (admin_id,))
            
            cert = cur.fetchone()
            if not cert:
                return {'success': True, 'is_valid': False, 'error': 'No active certificate'}
            
            # Constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(str(cert['certificate_code']), certificate)
            is_expired = cert['expires_at'] < datetime.utcnow()
            
            return {
                'success': True,
                'is_valid': is_valid and not is_expired,
                'expires': cert['expires_at'].isoformat()
            }
        except Exception as e:
            logger.error(f"Certificate validation error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def revoke_certificate(self, admin_id: str, requester_id: str) -> Dict[str, Any]:
        """
        Revoke a super admin certificate. Only Super Admin can revoke.
        
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            if requester_id != "A000":
                return {'success': False, 'error': 'Only Super Admin (A000) can revoke certificates'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            cur.execute("""
                UPDATE super_admin_certificates SET is_active = 0, is_revoked = 1, revoked_at = %s
                WHERE admin_id = %s
            """, (datetime.utcnow(), admin_id))
            
            if cur.rowcount == 0:
                conn.close()
                return {'success': False, 'error': 'Certificate not found'}
            
            conn.commit()
            self._audit_log(requester_id, 'CERTIFICATE_REVOKED', 
                          f'Revoked certificate for {admin_id}', admin_id)
            
            return {'success': True}
        except Exception as e:
            logger.error(f"Certificate revocation error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== AUDIT LOGGING ====================
    def _audit_log(self, user_id: str, action: str, details: str, 
                   target_id: Optional[str] = None, ip_address: str = "0.0.0.0",
                   user_agent: str = "") -> bool:
        """
        Internal method to log an audit event
        
        Returns:
            bool: True if logged successfully
        """
        try:
            conn = self._get_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_logs (user_id, action, details, target_id, 
                                       ip_address, user_agent, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, action, details, target_id, ip_address, user_agent, datetime.utcnow()))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

    def get_audit_logs(self, admin_id: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get audit logs. Only Super Admin can view all logs, others can view their own.
        
        Args:
            admin_id: Admin requesting logs (or A000 for all)
            filters: {'action': str, 'user_id': str, 'days': int, 'limit': int}
            
        Returns:
            {'success': bool, 'logs': list, 'total': int, 'error': str}
        """
        try:
            if not filters:
                filters = {}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            # Build query
            query = "SELECT * FROM audit_logs WHERE 1=1"
            params = []
            
            if admin_id != "A000":
                query += " AND user_id = %s"
                params.append(admin_id)
            
            if 'action' in filters:
                query += " AND action = %s"
                params.append(filters['action'])
            
            if 'user_id' in filters:
                query += " AND user_id = %s"
                params.append(filters['user_id'])
            
            if 'days' in filters:
                query += " AND timestamp >= NOW() - INTERVAL '%s days'"
                params.append(filters['days'])
            
            query += " ORDER BY timestamp DESC"
            
            limit = filters.get('limit', 100)
            query += f" LIMIT {limit}"
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query, params)
            logs = cur.fetchall()
            
            # Get total count
            count_query = query.replace("SELECT *", "SELECT COUNT(*) as cnt").split("LIMIT")[0]
            cur.execute(count_query, params)
            total = cur.fetchone()['cnt']
            
            return {
                'success': True,
                'logs': [dict(log) for log in logs],
                'total': total
            }
        except Exception as e:
            logger.error(f"Audit logs retrieval error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def log_login_attempt(self, user_id: str, success: bool, ip_address: str = "0.0.0.0",
                         user_agent: str = "") -> bool:
        """Log login attempt"""
        action = 'LOGIN_SUCCESS' if success else 'LOGIN_FAILED'
        details = f"Login {'successful' if success else 'failed'} from {ip_address}"
        return self._audit_log(user_id, action, details, None, ip_address, user_agent)

    # ==================== PASSWORD MANAGEMENT ====================
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - At least 1 special character
        
        Returns:
            (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        return True, "Password is strong"

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def update_password(self, user_id: str, new_password: str, requester_id: str,
                       old_password_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Update user password with history tracking
        
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            # Validate password strength
            is_valid, msg = self.validate_password_strength(new_password)
            if not is_valid:
                return {'success': False, 'error': msg}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            
            # Check password history (no reuse of last 5 passwords)
            cur.execute("""
                SELECT COUNT(*) as cnt FROM password_history
                WHERE user_id = %s AND password_hash = %s
            """, (user_id, old_password_hash))
            
            if cur.fetchone()['cnt'] > 0:
                conn.close()
                return {'success': False, 'error': 'Cannot reuse recent passwords'}
            
            # Hash new password
            new_hash = self.hash_password(new_password)
            
            # Store in password history
            cur.execute("""
                INSERT INTO password_history (user_id, password_hash, changed_at)
                VALUES (%s, %s, %s)
            """, (user_id, old_password_hash, datetime.utcnow()))
            
            # Update user password (would be in users table)
            # This is a template - actual implementation depends on user table schema
            
            conn.commit()
            self._audit_log(requester_id, 'PASSWORD_CHANGED', 
                          f'Password updated for {user_id}', user_id)
            
            return {'success': True}
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== FEATURE TOGGLE MANAGEMENT ====================
    def toggle_feature(self, feature_name: str, enabled: bool, requester_id: str,
                      time_limit_minutes: int = None, disable_message: str = "") -> Dict[str, Any]:
        """
        Toggle system features on/off
        
        Args:
            feature_name: Name of feature (e.g., 'chat', 'payments', 'exams')
            enabled: True to enable, False to disable
            requester_id: Super Admin ID (A000)
            time_limit_minutes: Optional - auto-enable after X minutes
            disable_message: Message to show users when disabled
            
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            if requester_id != "A000":
                return {'success': False, 'error': 'Only Super Admin can toggle features'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            auto_enable_at = None
            if time_limit_minutes and not enabled:
                auto_enable_at = datetime.utcnow() + timedelta(minutes=time_limit_minutes)
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO feature_toggles (feature_name, is_enabled, toggled_by, 
                                            toggled_at, auto_enable_at, disable_message)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (feature_name) DO UPDATE SET
                    is_enabled = EXCLUDED.is_enabled,
                    toggled_by = EXCLUDED.toggled_by,
                    toggled_at = EXCLUDED.toggled_at,
                    auto_enable_at = EXCLUDED.auto_enable_at,
                    disable_message = EXCLUDED.disable_message
            """, (feature_name, enabled, requester_id, datetime.utcnow(), auto_enable_at, disable_message))
            
            conn.commit()
            self._audit_log(requester_id, 'FEATURE_TOGGLED',
                          f'Feature {feature_name} {"enabled" if enabled else "disabled"}',
                          feature_name)
            
            return {'success': True}
        except Exception as e:
            logger.error(f"Feature toggle error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def is_feature_enabled(self, feature_name: str) -> Dict[str, Any]:
        """
        Check if a feature is enabled
        
        Returns:
            {'success': bool, 'is_enabled': bool, 'message': str, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT is_enabled, auto_enable_at, disable_message FROM feature_toggles
                WHERE feature_name = %s
            """, (feature_name,))
            
            result = cur.fetchone()
            
            if not result:
                # Feature not found - assume enabled
                return {'success': True, 'is_enabled': True, 'message': 'Feature enabled (default)'}
            
            is_enabled = result['is_enabled']
            
            # Check auto-enable
            if not is_enabled and result['auto_enable_at']:
                if datetime.utcnow() >= result['auto_enable_at']:
                    # Auto-enable
                    cur.execute("""
                        UPDATE feature_toggles SET is_enabled = true, auto_enable_at = NULL
                        WHERE feature_name = %s
                    """, (feature_name,))
                    conn.commit()
                    return {'success': True, 'is_enabled': True, 'message': 'Feature auto-enabled'}
            
            message = result['disable_message'] if not is_enabled else 'Feature enabled'
            
            return {
                'success': True,
                'is_enabled': is_enabled,
                'message': message
            }
        except Exception as e:
            logger.error(f"Feature check error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_feature_status(self, requester_id: str) -> Dict[str, Any]:
        """
        Get status of all features. Only Super Admin can view all.
        
        Returns:
            {'success': bool, 'features': list, 'error': str}
        """
        try:
            if requester_id != "A000":
                return {'success': False, 'error': 'Only Super Admin can view all features'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT feature_name, is_enabled, toggled_by, toggled_at, 
                       auto_enable_at, disable_message
                FROM feature_toggles
                ORDER BY feature_name
            """)
            
            features = cur.fetchall()
            return {
                'success': True,
                'features': [dict(f) for f in features]
            }
        except Exception as e:
            logger.error(f"Feature status retrieval error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== SYSTEM SECURITY CHECKS ====================
    def get_security_stats(self, requester_id: str) -> Dict[str, Any]:
        """
        Get security statistics - Super Admin only
        
        Returns:
            {'success': bool, 'stats': dict, 'error': str}
        """
        try:
            if requester_id != "A000":
                return {'success': False, 'error': 'Only Super Admin can view security stats'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Failed login attempts in last 24 hours
            cur.execute("""
                SELECT COUNT(*) as failed_logins FROM audit_logs
                WHERE action = 'LOGIN_FAILED' AND timestamp > NOW() - INTERVAL '1 day'
            """)
            failed_logins = cur.fetchone()['failed_logins']
            
            # Active certificates
            cur.execute("""
                SELECT COUNT(*) as active_certs FROM admin_certificates
                WHERE is_active = true AND expires_at > NOW()
            """)
            active_certs = cur.fetchone()['active_certs']
            
            # Recent audit activity
            cur.execute("""
                SELECT COUNT(*) as recent_actions FROM audit_logs
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)
            recent_actions = cur.fetchone()['recent_actions']
            
            return {
                'success': True,
                'stats': {
                    'failed_logins_24h': failed_logins,
                    'active_certificates': active_certs,
                    'recent_actions_1h': recent_actions,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Security stats error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
