"""
Dashboard Service - Teacher, Student, Admin Dashboard Implementations
Provides unified interfaces for key stakeholders
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import json

logger = logging.getLogger(__name__)


class DashboardService:
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

    # ==================== STUDENT DASHBOARD ====================
    
    def get_student_dashboard(self, student_id: str) -> Dict[str, Any]:
        """
        Get comprehensive student dashboard with:
        - Overall statistics
        - Recent exams
        - Performance metrics
        - Badges earned
        - Learning recommendations
        - Study streaks
        
        Returns:
            {'success': bool, 'dashboard': dict, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get student info
            cur.execute("""
                SELECT user_id, email, role, registration_date FROM users
                WHERE user_id = %s
            """, (student_id,))
            student = cur.fetchone()
            
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            # Get exam statistics
            cur.execute("""
                SELECT COUNT(*) as total_exams,
                       AVG(score::float / max_score * 100) as avg_percentage,
                       MAX(score::float / max_score * 100) as best_score,
                       MIN(score::float / max_score * 100) as worst_score
                FROM exam_submissions
                WHERE student_id = %s
            """, (student_id,))
            
            exam_stats = cur.fetchone() or {}
            
            # Get recent exams (last 5)
            cur.execute("""
                SELECT es.exam_id, e.exam_name, es.score, es.max_score,
                       es.submitted_at, e.subject
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s
                ORDER BY es.submitted_at DESC
                LIMIT 5
            """, (student_id,))
            
            recent_exams = [dict(r) for r in cur.fetchall()]
            
            # Get badges earned
            cur.execute("""
                SELECT b.badge_id, b.badge_name, b.emoji, ab.earned_at
                FROM awarded_badges ab
                JOIN badges b ON ab.badge_id = b.id
                WHERE ab.student_id = %s
                ORDER BY ab.earned_at DESC
                LIMIT 10
            """, (student_id,))
            
            badges = [dict(b) for b in cur.fetchall()]
            
            # Get study streak
            cur.execute("""
                SELECT COUNT(DISTINCT CAST(submitted_at AS DATE)) as days_active
                FROM exam_submissions
                WHERE student_id = %s
                AND submitted_at > NOW() - INTERVAL '30 days'
            """, (student_id,))
            
            streak = cur.fetchone()
            days_active = streak['days_active'] if streak else 0
            
            # Get total points
            cur.execute("""
                SELECT COALESCE(SUM(points_earned), 0) as total_points
                FROM student_points
                WHERE student_id = %s
            """, (student_id,))
            
            points = cur.fetchone()
            
            dashboard = {
                'student_info': {
                    'user_id': student['user_id'],
                    'email': student['email'],
                    'registration_date': student['registration_date'].isoformat() if student['registration_date'] else None,
                    'member_since_days': (datetime.utcnow() - student['registration_date']).days if student['registration_date'] else 0
                },
                'statistics': {
                    'total_exams': exam_stats.get('total_exams', 0),
                    'avg_percentage': round(exam_stats.get('avg_percentage', 0), 2),
                    'best_score': round(exam_stats.get('best_score', 0), 2),
                    'worst_score': round(exam_stats.get('worst_score', 0), 2),
                    'total_points': points['total_points'] if points else 0,
                    'badges_earned': len(badges),
                    'study_days_30d': days_active
                },
                'recent_exams': recent_exams[:5],
                'badges': badges[:5],
                'performance_level': self._get_performance_level(exam_stats.get('avg_percentage', 0))
            }
            
            return {'success': True, 'dashboard': dashboard}
        
        except Exception as e:
            logger.error(f"Student dashboard error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_student_portfolio(self, student_id: str) -> Dict[str, Any]:
        """
        Get student portfolio for sharing
        - Certificates
        - Badges
        - Academic achievements
        - Public profile info
        
        Returns:
            {'success': bool, 'portfolio': dict, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get public profile
            cur.execute("""
                SELECT user_id, first_name, last_name FROM users
                WHERE user_id = %s AND role = 'student'
            """, (student_id,))
            
            student = cur.fetchone()
            if not student:
                return {'success': False, 'error': 'Student not found'}
            
            # Get certificates
            cur.execute("""
                SELECT cert_id, cert_name, issued_date, course_name
                FROM certificates
                WHERE student_id = %s AND is_verified = true
                ORDER BY issued_date DESC
            """, (student_id,))
            
            certificates = [dict(c) for c in cur.fetchall()]
            
            # Get badges
            cur.execute("""
                SELECT b.badge_name, b.emoji, ab.earned_at, b.description
                FROM awarded_badges ab
                JOIN badges b ON ab.badge_id = b.id
                WHERE ab.student_id = %s
                ORDER BY ab.earned_at DESC
            """, (student_id,))
            
            badges = [dict(b) for b in cur.fetchall()]
            
            # Get achievements (high exam scores)
            cur.execute("""
                SELECT e.exam_name, e.subject, 
                       ROUND(es.score::float / es.max_score * 100, 2) as percentage,
                       es.submitted_at
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s AND es.score::float / es.max_score >= 0.85
                ORDER BY es.submitted_at DESC
                LIMIT 10
            """, (student_id,))
            
            achievements = [dict(a) for a in cur.fetchall()]
            
            portfolio = {
                'name': f"{student['first_name']} {student['last_name']}",
                'user_id': student['user_id'],
                'certificates': certificates,
                'badges': badges,
                'high_achievements': achievements
            }
            
            return {'success': True, 'portfolio': portfolio}
        
        except Exception as e:
            logger.error(f"Portfolio error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== TEACHER DASHBOARD ====================
    
    def get_teacher_dashboard(self, teacher_id: str) -> Dict[str, Any]:
        """
        Get teacher dashboard with:
        - Classes overview
        - Student statistics
        - Recent exams created
        - Marking pending
        - Class performance
        
        Returns:
            {'success': bool, 'dashboard': dict, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get teacher info
            cur.execute("""
                SELECT user_id, first_name, last_name FROM users
                WHERE user_id = %s AND role = 'teacher'
            """, (teacher_id,))
            
            teacher = cur.fetchone()
            if not teacher:
                return {'success': False, 'error': 'Teacher not found'}
            
            # Get classes
            cur.execute("""
                SELECT class_id, class_name, subject, level
                FROM classes
                WHERE teacher_id = %s
                ORDER BY class_name
            """, (teacher_id,))
            
            classes = [dict(c) for c in cur.fetchall()]
            
            # Get total students
            cur.execute("""
                SELECT COUNT(DISTINCT student_id) as total_students
                FROM class_enrollments ce
                JOIN classes c ON ce.class_id = c.id
                WHERE c.teacher_id = %s
            """, (teacher_id,))
            
            student_count = cur.fetchone()
            
            # Get pending marking count
            cur.execute("""
                SELECT COUNT(*) as pending_marks
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE e.teacher_id = %s AND es.status = 'submitted'
                AND es.essay_grade IS NULL
            """, (teacher_id,))
            
            pending_marks = cur.fetchone()
            
            # Get recent exams
            cur.execute("""
                SELECT exam_id, exam_name, subject, created_at, total_questions
                FROM exams
                WHERE teacher_id = %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (teacher_id,))
            
            recent_exams = [dict(e) for e in cur.fetchall()]
            
            # Get class performance
            class_performance = []
            for cls in classes:
                cur.execute("""
                    SELECT AVG(es.score::float / es.max_score * 100) as avg_percentage
                    FROM exam_submissions es
                    JOIN exams e ON es.exam_id = e.id
                    JOIN class_enrollments ce ON es.student_id = ce.student_id
                    WHERE ce.class_id = %s AND e.teacher_id = %s
                """, (cls['class_id'], teacher_id))
                
                perf = cur.fetchone()
                class_performance.append({
                    'class_name': cls['class_name'],
                    'subject': cls['subject'],
                    'avg_performance': round(perf['avg_percentage'], 2) if perf and perf['avg_percentage'] else 0
                })
            
            dashboard = {
                'teacher_info': {
                    'name': f"{teacher['first_name']} {teacher['last_name']}",
                    'user_id': teacher['user_id']
                },
                'statistics': {
                    'total_classes': len(classes),
                    'total_students': student_count['total_students'] if student_count else 0,
                    'pending_marking': pending_marks['pending_marks'] if pending_marks else 0
                },
                'classes': classes,
                'class_performance': class_performance,
                'recent_exams': recent_exams,
                'action_items': {
                    'pending_marking': pending_marks['pending_marks'] if pending_marks else 0,
                    'student_messages': 0  # Placeholder
                }
            }
            
            return {'success': True, 'dashboard': dashboard}
        
        except Exception as e:
            logger.error(f"Teacher dashboard error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_exam_marking_dashboard(self, teacher_id: str, exam_id: str) -> Dict[str, Any]:
        """
        Get detailed marking dashboard for specific exam
        - Submissions to mark
        - Student answers
        - Marking interface data
        
        Returns:
            {'success': bool, 'marking_data': dict, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Verify teacher owns this exam
            cur.execute("""
                SELECT exam_id, exam_name FROM exams
                WHERE exam_id = %s AND teacher_id = %s
            """, (exam_id, teacher_id))
            
            exam = cur.fetchone()
            if not exam:
                return {'success': False, 'error': 'Exam not found or unauthorized'}
            
            # Get pending submissions
            cur.execute("""
                SELECT es.submission_id, es.student_id, u.first_name, u.last_name,
                       es.score, es.max_score, es.submitted_at, es.status
                FROM exam_submissions es
                JOIN users u ON es.student_id = u.user_id
                WHERE es.exam_id = %s AND es.status = 'submitted'
                ORDER BY es.submitted_at ASC
                LIMIT 50
            """, (exam_id,))
            
            submissions = [dict(s) for s in cur.fetchall()]
            
            # Get answer breakdowns per question
            cur.execute("""
                SELECT q.question_id, q.question_text, q.question_type,
                       COUNT(DISTINCT sa.submission_id) as total_answered
                FROM questions q
                LEFT JOIN student_answers sa ON q.question_id = sa.question_id
                WHERE q.exam_id = %s
                GROUP BY q.question_id, q.question_text, q.question_type
            """, (exam_id,))
            
            questions = [dict(q) for q in cur.fetchall()]
            
            marking_data = {
                'exam': {
                    'exam_id': exam['exam_id'],
                    'exam_name': exam['exam_name']
                },
                'submissions': submissions,
                'questions': questions,
                'stats': {
                    'total_submissions': len(submissions),
                    'pending_marking': len([s for s in submissions if s['status'] == 'submitted']),
                    'marked': len([s for s in submissions if s['status'] == 'graded'])
                }
            }
            
            return {'success': True, 'marking_data': marking_data}
        
        except Exception as e:
            logger.error(f"Marking dashboard error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== ADMIN DASHBOARD ====================
    
    def get_admin_dashboard(self, admin_id: str) -> Dict[str, Any]:
        """
        Get admin dashboard with:
        - System overview
        - User statistics
        - Security alerts
        - Feature status
        - System health
        
        Returns:
            {'success': bool, 'dashboard': dict, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get user statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    SUM(CASE WHEN role = 'student' THEN 1 ELSE 0 END) as total_students,
                    SUM(CASE WHEN role = 'teacher' THEN 1 ELSE 0 END) as total_teachers,
                    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as total_admins
                FROM users
            """)
            
            user_stats = cur.fetchone()
            
            # Get active users (last 24h)
            cur.execute("""
                SELECT COUNT(DISTINCT user_id) as active_24h
                FROM audit_logs
                WHERE timestamp > NOW() - INTERVAL '1 day'
            """)
            
            active_users = cur.fetchone()
            
            # Get system metrics
            cur.execute("""
                SELECT cpu_usage, memory_usage, active_users, api_response_time_ms
                FROM system_health_metrics
                ORDER BY recorded_at DESC
                LIMIT 1
            """)
            
            health = cur.fetchone()
            
            # Get security alerts
            cur.execute("""
                SELECT action, COUNT(*) as count
                FROM audit_logs
                WHERE timestamp > NOW() - INTERVAL '24 hours'
                AND action IN ('LOGIN_FAILED', 'UNAUTHORIZED_ACCESS', 'PLAGIARISM_DETECTED')
                GROUP BY action
            """)
            
            security_alerts = [dict(s) for s in cur.fetchall()]
            
            # Get feature status
            cur.execute("""
                SELECT feature_name, is_enabled FROM feature_toggles
            """)
            
            features = [dict(f) for f in cur.fetchall()]
            
            # Get failed logins (last 24h)
            cur.execute("""
                SELECT COUNT(*) as failed_logins
                FROM audit_logs
                WHERE action = 'LOGIN_FAILED'
                AND timestamp > NOW() - INTERVAL '1 day'
            """)
            
            failed_logins = cur.fetchone()
            
            dashboard = {
                'overview': {
                    'total_users': user_stats['total_users'],
                    'total_students': user_stats['total_students'],
                    'total_teachers': user_stats['total_teachers'],
                    'active_24h': active_users['active_24h']
                },
                'system_health': {
                    'cpu_usage': health['cpu_usage'] if health else 0,
                    'memory_usage': health['memory_usage'] if health else 0,
                    'active_users': health['active_users'] if health else 0,
                    'api_response_ms': health['api_response_time_ms'] if health else 0,
                    'status': self._get_health_status(health) if health else 'unknown'
                },
                'security': {
                    'failed_logins_24h': failed_logins['failed_logins'] if failed_logins else 0,
                    'alerts': security_alerts
                },
                'features': features
            }
            
            return {'success': True, 'dashboard': dashboard}
        
        except Exception as e:
            logger.error(f"Admin dashboard error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_system_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive system analytics
        - User growth
        - Exam statistics
        - Subject performance
        - Feature usage
        
        Returns:
            {'success': bool, 'analytics': dict, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get subject-wise performance
            cur.execute("""
                SELECT e.subject, 
                       COUNT(*) as exams_taken,
                       AVG(es.score::float / es.max_score * 100) as avg_percentage
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                GROUP BY e.subject
                ORDER BY avg_percentage DESC
            """)
            
            subject_stats = [dict(s) for s in cur.fetchall()]
            
            # Get exam type statistics
            cur.execute("""
                SELECT e.exam_type,
                       COUNT(*) as total_exams,
                       COUNT(DISTINCT e.teacher_id) as teachers,
                       COUNT(DISTINCT es.student_id) as students_participated
                FROM exams e
                LEFT JOIN exam_submissions es ON e.exam_id = es.exam_id
                GROUP BY e.exam_type
            """)
            
            exam_stats = [dict(e) for e in cur.fetchall()]
            
            # Get user growth (weekly)
            cur.execute("""
                SELECT DATE_TRUNC('week', registration_date)::DATE as week,
                       COUNT(*) as new_users
                FROM users
                WHERE registration_date > NOW() - INTERVAL '12 weeks'
                GROUP BY DATE_TRUNC('week', registration_date)
                ORDER BY week DESC
            """)
            
            growth = [dict(g) for g in cur.fetchall()]
            
            # Get most popular badges
            cur.execute("""
                SELECT b.badge_name, b.emoji,
                       COUNT(ab.badge_id) as times_awarded
                FROM awarded_badges ab
                JOIN badges b ON ab.badge_id = b.id
                GROUP BY b.badge_id, b.badge_name, b.emoji
                ORDER BY times_awarded DESC
                LIMIT 10
            """)
            
            badges = [dict(b) for b in cur.fetchall()]
            
            analytics = {
                'subject_statistics': subject_stats,
                'exam_statistics': exam_stats,
                'user_growth': growth,
                'popular_badges': badges
            }
            
            return {'success': True, 'analytics': analytics}
        
        except Exception as e:
            logger.error(f"Analytics error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== HELPER METHODS ====================
    
    def _get_performance_level(self, avg_percentage: float) -> str:
        """Determine performance level based on average percentage"""
        if avg_percentage >= 90:
            return 'Excellent'
        elif avg_percentage >= 80:
            return 'Good'
        elif avg_percentage >= 70:
            return 'Satisfactory'
        elif avg_percentage >= 60:
            return 'Fair'
        else:
            return 'Needs Improvement'

    def _get_health_status(self, health: Dict) -> str:
        """Determine system health status"""
        if health['cpu_usage'] > 90 or health['memory_usage'] > 90:
            return 'critical'
        elif health['cpu_usage'] > 75 or health['memory_usage'] > 75:
            return 'warning'
        else:
            return 'healthy'
