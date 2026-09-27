"""
Certificates & Gamification Service Module
Handles badges, certificates, achievements, and student portfolios
"""

import json
import uuid
from datetime import datetime
import psycopg2
import psycopg2.extras

class CertificationService:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def create_badge_template(self, badge_name, badge_code, description, icon_path, 
                             emoji_code, color_hex='#FFD700', points=100):
        """Create badge template"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO badge_templates 
                (badge_name, badge_code, description, icon_path, emoji_code, 
                 color_hex, points_value, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                RETURNING id
            """, (badge_name, badge_code, description, icon_path, emoji_code, 
                  color_hex, points))
            
            badge_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'badge_id': badge_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def add_achievement_criteria(self, badge_id, criteria_name, criteria_type, 
                                criteria_value, threshold_value):
        """Add criteria for earning badge"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO achievement_criteria 
                (badge_id, criteria_name, criteria_type, criteria_value, threshold_value)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (badge_id, criteria_name, criteria_type, criteria_value, threshold_value))
            
            criteria_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'criteria_id': criteria_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def award_badge(self, student_id, badge_id, criteria_id=None):
        """Award badge to student"""
        try:
            cur = self.db.cursor()
            
            # Check if already awarded
            cur.execute("""
                SELECT id FROM student_badges_awarded 
                WHERE student_id = %s AND badge_id = %s
            """, (student_id, badge_id))
            
            if cur.fetchone():
                cur.close()
                return {'success': False, 'error': 'Badge already awarded'}
            
            # Award badge
            cur.execute("""
                INSERT INTO student_badges_awarded 
                (student_id, badge_id, earned_by_criteria_id)
                VALUES (%s, %s, %s)
            """, (student_id, badge_id, criteria_id))
            
            # Get badge points
            cur.execute("SELECT points_value FROM badge_templates WHERE id = %s", (badge_id,))
            points = cur.fetchone()[0]
            
            # Update portfolio
            cur.execute("""
                UPDATE student_portfolio 
                SET total_points = total_points + %s,
                    total_achievements = total_achievements + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE student_id = %s
            """, (points, student_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'points_awarded': points}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_student_badges(self, student_id):
        """Get student's earned badges"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT bt.id, bt.badge_name, bt.emoji_code, bt.color_hex, 
                    bt.points_value, sba.awarded_at
                FROM student_badges_awarded sba
                JOIN badge_templates bt ON sba.badge_id = bt.id
                WHERE sba.student_id = %s
                ORDER BY sba.awarded_at DESC
            """, (student_id,))
            
            badges = cur.fetchall()
            cur.close()
            
            return {'success': True, 'badges': [dict(b) for b in badges]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_certificate_template(self, template_name, template_path, 
                                   variables, teacher_id, description=""):
        """Create certificate template"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            variables_json = json.dumps(variables) if isinstance(variables, list) else variables
            
            cur.execute("""
                INSERT INTO certificate_templates 
                (template_name, description, template_path, variables, created_by)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (template_name, description, template_path, variables_json, teacher_id))
            
            template_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'template_id': template_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def issue_certificate(self, student_id, template_id, achievement_type, 
                         teacher_id, custom_data=None):
        """Issue certificate to student"""
        try:
            certificate_id = f"CERT-{uuid.uuid4().hex[:16]}"
            verification_code = str(uuid.uuid4().hex[:8]).upper()
            
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO certificates_issued 
                (certificate_id, student_id, template_id, achievement_type, 
                 issued_by, verification_code)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (certificate_id, student_id, template_id, achievement_type, 
                  teacher_id, verification_code))
            
            self.db.commit()
            cur.close()
            
            return {
                'success': True,
                'certificate_id': certificate_id,
                'verification_code': verification_code
            }
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_student_certificates(self, student_id):
        """Get student's certificates"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT ci.certificate_id, ci.achievement_type, ct.template_name,
                    ci.issued_at, ci.verification_code, ci.is_revoked
                FROM certificates_issued ci
                JOIN certificate_templates ct ON ci.template_id = ct.id
                WHERE ci.student_id = %s AND ci.is_revoked = 0
                ORDER BY ci.issued_at DESC
            """, (student_id,))
            
            certificates = cur.fetchall()
            cur.close()
            
            return {'success': True, 'certificates': [dict(c) for c in certificates]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_or_create_portfolio(self, student_id):
        """Get or create student portfolio"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Check if exists
            cur.execute("SELECT * FROM student_portfolio WHERE student_id = %s", (student_id,))
            portfolio = cur.fetchone()
            
            if not portfolio:
                # Create new portfolio
                cur.execute("""
                    INSERT INTO student_portfolio 
                    (student_id, total_points, total_achievements)
                    VALUES (%s, 0, 0)
                """, (student_id,))
                self.db.commit()
                
                cur.execute("SELECT * FROM student_portfolio WHERE student_id = %s", (student_id,))
                portfolio = cur.fetchone()
            
            # Get badges and certificates
            cur.execute("""
                SELECT COUNT(*) as count FROM student_badges_awarded WHERE student_id = %s
            """, (student_id,))
            badge_count = cur.fetchone()['count']
            
            cur.execute("""
                SELECT COUNT(*) as count FROM certificates_issued 
                WHERE student_id = %s AND is_revoked = 0
            """, (student_id,))
            cert_count = cur.fetchone()['count']
            
            cur.close()
            
            portfolio_dict = dict(portfolio)
            portfolio_dict['badge_count'] = badge_count
            portfolio_dict['certificate_count'] = cert_count
            
            return {'success': True, 'portfolio': portfolio_dict}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_badge_criteria(self, student_id, badge_id):
        """Check if student meets badge criteria"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get criteria
            cur.execute("""
                SELECT * FROM achievement_criteria WHERE badge_id = %s
            """, (badge_id,))
            
            criteria_list = cur.fetchall()
            
            for criteria in criteria_list:
                criteria_type = criteria['criteria_type']
                threshold = criteria['threshold_value']
                
                if criteria_type == 'score_threshold':
                    # Check student's average score
                    cur.execute("""
                        SELECT AVG(percentage) as avg_score 
                        FROM exam_submissions 
                        WHERE student_id = %s AND status = 'graded'
                    """, (student_id,))
                    
                    result = cur.fetchone()
                    avg_score = result['avg_score'] if result['avg_score'] else 0
                    
                    if avg_score < threshold:
                        cur.close()
                        return {'meets_criteria': False, 'reason': f'Average score {avg_score} below {threshold}'}
                
                elif criteria_type == 'completion_count':
                    # Check submissions count
                    cur.execute("""
                        SELECT COUNT(*) as count FROM exam_submissions 
                        WHERE student_id = %s
                    """, (student_id,))
                    
                    count = cur.fetchone()['count']
                    
                    if count < threshold:
                        cur.close()
                        return {'meets_criteria': False, 'reason': f'Completed {count} tests, need {threshold}'}
                
                elif criteria_type == 'streak':
                    # Check consecutive passing scores
                    cur.execute("""
                        SELECT COUNT(*) as consecutive 
                        FROM (
                            SELECT * FROM exam_submissions 
                            WHERE student_id = %s AND percentage >= 50
                            ORDER BY submitted_at DESC
                            LIMIT %s
                        ) sub
                    """, (student_id, int(threshold)))
                    
                    streak = cur.fetchone()['consecutive']
                    
                    if streak < threshold:
                        cur.close()
                        return {'meets_criteria': False, 'reason': f'Streak of {streak}, need {threshold}'}
            
            cur.close()
            return {'meets_criteria': True}
        except Exception as e:
            return {'meets_criteria': False, 'error': str(e)}
    
    def revoke_certificate(self, certificate_id, teacher_id):
        """Revoke issued certificate"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE certificates_issued 
                SET is_revoked = 1
                WHERE certificate_id = %s
            """, (certificate_id,))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def verify_certificate(self, certificate_id, verification_code):
        """Verify certificate authenticity"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT ci.certificate_id, ci.student_id, ci.achievement_type,
                    ci.issued_at, ct.template_name, s.fullName, ci.is_revoked
                FROM certificates_issued ci
                JOIN certificate_templates ct ON ci.template_id = ct.id
                JOIN students s ON ci.student_id = s.id
                WHERE ci.certificate_id = %s AND ci.verification_code = %s
            """, (certificate_id, verification_code))
            
            cert = cur.fetchone()
            cur.close()
            
            if not cert:
                return {'valid': False, 'error': 'Certificate not found or invalid code'}
            
            if cert['is_revoked']:
                return {'valid': False, 'error': 'Certificate has been revoked'}
            
            return {
                'valid': True,
                'certificate': dict(cert)
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}

# Initialize service
certification_service = None

def init_certification_service(db_connection):
    global certification_service
    certification_service = CertificationService(db_connection)
    return certification_service
