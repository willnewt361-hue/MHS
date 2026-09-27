"""
Assessment & Exam Service Module
Handles exam creation, student submissions, grading, and performance analysis
"""

import json
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

class AssessmentService:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def create_exam(self, exam_name, subject, academic_level, teacher_id, 
                   total_marks, duration_minutes, exam_type='quiz', instructions=""):
        """Create a new exam"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO exams (exam_name, subject, academic_level, created_by, 
                    total_marks, duration_minutes, exam_type, instructions)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (exam_name, subject, academic_level, teacher_id, total_marks, 
                  duration_minutes, exam_type, instructions))
            
            exam_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'exam_id': exam_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def add_question(self, exam_id, question_text, question_type, marks, 
                    options=None, correct_answer=None, explanation="", difficulty="medium"):
        """Add question to exam"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get next position
            cur.execute("SELECT COUNT(*) as count FROM questions WHERE exam_id = %s", (exam_id,))
            position = cur.fetchone()['count'] + 1
            
            options_json = json.dumps(options) if options else None
            
            cur.execute("""
                INSERT INTO questions (exam_id, question_text, question_type, marks, 
                    options, correct_answer, explanation, difficulty_level, question_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (exam_id, question_text, question_type, marks, options_json, 
                  correct_answer, explanation, difficulty, position))
            
            question_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'question_id': question_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def start_exam_session(self, exam_id, student_id):
        """Start exam session for student"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Check existing active submission
            cur.execute("""
                SELECT id FROM exam_submissions 
                WHERE exam_id = %s AND student_id = %s AND status = 'in_progress'
            """, (exam_id, student_id))
            
            existing = cur.fetchone()
            if existing:
                cur.close()
                return {'success': True, 'submission_id': existing['id']}
            
            # Create new submission
            cur.execute("""
                INSERT INTO exam_submissions (exam_id, student_id, start_time, status)
                VALUES (%s, %s, CURRENT_TIMESTAMP, 'in_progress')
                RETURNING id
            """, (exam_id, student_id))
            
            submission_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'submission_id': submission_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def submit_answer(self, submission_id, question_id, student_answer):
        """Submit answer to question"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO exam_answers (submission_id, question_id, student_answer, answered_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (submission_id, question_id) DO UPDATE SET
                    student_answer = EXCLUDED.student_answer,
                    answered_at = CURRENT_TIMESTAMP
            """, (submission_id, question_id, student_answer))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def auto_grade_submission(self, submission_id):
        """Automatically grade objective questions"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get all answers for submission
            cur.execute("""
                SELECT ea.id, ea.question_id, ea.student_answer, q.correct_answer, q.marks
                FROM exam_answers ea
                JOIN questions q ON ea.question_id = q.id
                WHERE ea.submission_id = %s AND q.question_type IN ('multiple_choice', 'true_false')
            """, (submission_id,))
            
            answers = cur.fetchall()
            total_marks = 0
            
            for answer in answers:
                is_correct = answer['student_answer'] == answer['correct_answer']
                marks = answer['marks'] if is_correct else 0
                total_marks += marks
                
                cur.execute("""
                    UPDATE exam_answers 
                    SET is_correct = %s, marks_awarded = %s
                    WHERE id = %s
                """, (1 if is_correct else 0, marks, answer['id']))
            
            # Get essay/short answer count
            cur.execute("""
                SELECT COUNT(*) as count FROM exam_answers ea
                JOIN questions q ON ea.question_id = q.id
                WHERE ea.submission_id = %s AND q.question_type IN ('essay', 'short_answer')
            """, (submission_id,))
            
            essay_count = cur.fetchone()['count']
            status = 'graded' if essay_count == 0 else 'submitted'
            
            # Update submission
            cur.execute("""
                SELECT total_marks FROM exams WHERE id = (
                    SELECT exam_id FROM exam_submissions WHERE id = %s
                )
            """, (submission_id,))
            
            max_marks = cur.fetchone()['total_marks']
            percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
            
            cur.execute("""
                UPDATE exam_submissions 
                SET total_score = %s, max_score = %s, percentage = %s, 
                    status = %s, submitted_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (total_marks, max_marks, percentage, status, submission_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'total_score': total_marks, 'percentage': percentage}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def submit_exam(self, submission_id):
        """Submit completed exam"""
        try:
            cur = self.db.cursor()
            
            # Auto-grade objective questions
            auto_grade = self.auto_grade_submission(submission_id)
            
            if not auto_grade['success']:
                return auto_grade
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'score': auto_grade['total_score']}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def grade_essay(self, answer_id, marks_awarded, teacher_id, feedback=""):
        """Grade essay/short answer question"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE exam_answers 
                SET marks_awarded = %s
                WHERE id = %s
            """, (marks_awarded, answer_id))
            
            # Record marking record
            cur.execute("""
                SELECT submission_id FROM exam_answers WHERE id = %s
            """, (answer_id,))
            
            submission_id = cur.fetchone()[0]
            
            cur.execute("""
                INSERT INTO teacher_marking_records 
                (submission_id, teacher_id, feedback, marks_awarded)
                VALUES (%s, %s, %s, %s)
            """, (submission_id, teacher_id, feedback, marks_awarded))
            
            # Recalculate submission total
            cur.execute("""
                UPDATE exam_submissions 
                SET total_score = (
                    SELECT COALESCE(SUM(marks_awarded), 0) FROM exam_answers 
                    WHERE submission_id = %s
                ),
                status = 'graded'
                WHERE id = %s
            """, (submission_id, submission_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_exam_questions(self, exam_id):
        """Get all questions for an exam"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, question_text, question_type, marks, options, 
                    explanation, difficulty_level, question_order
                FROM questions
                WHERE exam_id = %s
                ORDER BY question_order
            """, (exam_id,))
            
            questions = cur.fetchall()
            cur.close()
            
            result_list = []
            for q in questions:
                q_dict = dict(q)
                if q_dict.get('options'):
                    q_dict['options'] = json.loads(q_dict['options'])
                result_list.append(q_dict)
            
            return {'success': True, 'questions': result_list}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_student_performance(self, student_id):
        """Get student's exam performance"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT es.id, e.exam_name, es.total_score, es.max_score, 
                    es.percentage, es.submitted_at, e.subject
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s AND es.status = 'graded'
                ORDER BY es.submitted_at DESC
            """, (student_id,))
            
            submissions = cur.fetchall()
            
            # Calculate stats
            cur.execute("""
                SELECT AVG(percentage) as avg_score, 
                    COUNT(*) as total_exams,
                    SUM(CASE WHEN percentage >= 50 THEN 1 ELSE 0 END) as passed_exams
                FROM exam_submissions
                WHERE student_id = %s AND status = 'graded'
            """, (student_id,))
            
            stats = cur.fetchone()
            cur.close()
            
            return {
                'success': True, 
                'submissions': [dict(s) for s in submissions],
                'stats': dict(stats) if stats else {}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def add_question_to_bank(self, question_text, subject, question_type, 
                            marks, options=None, correct_answer=None, 
                            difficulty="medium", teacher_id=None, is_public=False):
        """Add question to reusable question bank"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            options_json = json.dumps(options) if options else None
            
            cur.execute("""
                INSERT INTO question_bank 
                (question_text, subject, question_type, marks, options, 
                 correct_answer, difficulty_level, created_by, is_public)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (question_text, subject, question_type, marks, options_json, 
                  correct_answer, difficulty, teacher_id, 1 if is_public else 0))
            
            question_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'question_id': question_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_question_bank(self, subject=None, difficulty=None, teacher_id=None):
        """Get questions from question bank"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            query = "SELECT * FROM question_bank WHERE (is_public = 1"
            params = []
            
            if teacher_id:
                query += " OR created_by = %s"
                params.append(teacher_id)
            
            query += ")"
            
            if subject:
                query += " AND subject = %s"
                params.append(subject)
            
            if difficulty:
                query += " AND difficulty_level = %s"
                params.append(difficulty)
            
            query += " ORDER BY created_at DESC"
            
            cur.execute(query, params)
            questions = cur.fetchall()
            
            result_list = []
            for q in questions:
                q_dict = dict(q)
                if q_dict.get('options'):
                    q_dict['options'] = json.loads(q_dict['options'])
                result_list.append(q_dict)
            
            cur.close()
            
            return {'success': True, 'questions': result_list}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_marking_style(self, teacher_id, time_period_days=30):
        """Analyze teacher's marking patterns"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get marking records within period
            cur.execute("""
                SELECT tmr.marks_awarded, q.marks, 
                    COUNT(*) as frequency
                FROM teacher_marking_records tmr
                JOIN exam_answers ea ON tmr.submission_id = ea.submission_id
                JOIN questions q ON ea.question_id = q.id
                WHERE tmr.teacher_id = %s
                AND tmr.marking_time > CURRENT_TIMESTAMP - INTERVAL '%s days'
                GROUP BY tmr.marks_awarded, q.marks
            """, (teacher_id, time_period_days))
            
            records = cur.fetchall()
            
            # Calculate stats
            cur.execute("""
                SELECT AVG(marks_awarded) as avg_awarded, 
                    MIN(marks_awarded) as min_awarded,
                    MAX(marks_awarded) as max_awarded,
                    STDDEV(marks_awarded) as std_dev,
                    COUNT(*) as total_marked
                FROM teacher_marking_records
                WHERE teacher_id = %s
                AND marking_time > CURRENT_TIMESTAMP - INTERVAL '%s days'
            """, (teacher_id, time_period_days))
            
            stats = cur.fetchone()
            cur.close()
            
            return {
                'success': True,
                'marking_records': [dict(r) for r in records],
                'stats': dict(stats) if stats else {}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize service
assessment_service = None

def init_assessment_service(db_connection):
    global assessment_service
    assessment_service = AssessmentService(db_connection)
    return assessment_service
