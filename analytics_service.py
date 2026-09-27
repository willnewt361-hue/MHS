"""
Advanced AI & Analytics Service - Multi-Model Fallback, Performance Analysis, Plagiarism Detection
Handles: AI analysis, student performance analytics, plagiarism detection, learning recommendations
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
import difflib

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db_connection_string: str):
        self.db_conn_string = db_connection_string
        self.models = {
            'primary': os.getenv('HUGGINGFACE_API_KEY'),  # Hugging Face or custom
            'secondary': os.getenv('ANTHROPIC_API_KEY'),  # Anthropic
            'tertiary': os.getenv('GOOGLE_API_KEY'),      # Google Gemini
        }
        self.local_model = "gpt4all"  # Final fallback

    def _get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return None

    # ==================== MULTI-MODEL FALLBACK SYSTEM ====================
    
    def _call_model(self, prompt: str, model_type: str = 'primary', 
                   max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Call AI model with fallback strategy
        
        Fallback chain:
        1. Primary (Hugging Face)
        2. Secondary (Anthropic)
        3. Tertiary (Google Gemini)
        4. Local (GPT4All)
        
        Args:
            prompt: The prompt to send to model
            model_type: primary, secondary, tertiary, local
            max_tokens: Max tokens in response
            
        Returns:
            {'success': bool, 'response': str, 'model_used': str, 'error': str}
        """
        try:
            # Try primary model (Hugging Face)
            if self.models['primary']:
                try:
                    result = self._call_hugging_face(prompt, max_tokens)
                    if result['success']:
                        return {'success': True, 'response': result['response'], 
                               'model_used': 'huggingface'}
                except Exception as e:
                    logger.warning(f"HuggingFace failed: {str(e)}, trying secondary...")
            
            # Try secondary model (Anthropic)
            if self.models['secondary']:
                try:
                    result = self._call_anthropic(prompt, max_tokens)
                    if result['success']:
                        return {'success': True, 'response': result['response'], 
                               'model_used': 'anthropic'}
                except Exception as e:
                    logger.warning(f"Anthropic failed: {str(e)}, trying tertiary...")
            
            # Try tertiary model (Google Gemini)
            if self.models['tertiary']:
                try:
                    result = self._call_google_gemini(prompt, max_tokens)
                    if result['success']:
                        return {'success': True, 'response': result['response'], 
                               'model_used': 'google_gemini'}
                except Exception as e:
                    logger.warning(f"Google Gemini failed: {str(e)}, falling back to local...")
            
            # Fallback to local model (GPT4All)
            result = self._call_gpt4all_local(prompt, max_tokens)
            if result['success']:
                return {'success': True, 'response': result['response'], 
                       'model_used': 'gpt4all_local'}
            
            return {'success': False, 'error': 'All models failed', 'model_used': 'none'}
        
        except Exception as e:
            logger.error(f"Model call error: {str(e)}")
            return {'success': False, 'error': str(e), 'model_used': 'none'}

    def _call_hugging_face(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Call Hugging Face API"""
        try:
            import requests
            api_url = "https://api-inference.huggingface.co/models/gpt2"
            headers = {"Authorization": f"Bearer {self.models['primary']}"}
            payload = {
                "inputs": prompt,
                "parameters": {"max_length": max_tokens}
            }
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                text = result[0]['generated_text'] if result else ""
                return {'success': True, 'response': text}
            elif response.status_code == 429:
                return {'success': False, 'error': 'Rate limited'}
            else:
                return {'success': False, 'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _call_anthropic(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.models['secondary'])
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return {'success': True, 'response': message.content[0].text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _call_google_gemini(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Call Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.models['tertiary'])
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return {'success': True, 'response': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _call_gpt4all_local(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """Call local GPT4All model"""
        try:
            from gpt4all import GPT4All
            model = GPT4All("ggml-gpt4all-j-v1.3-groovy")
            response = model.generate(prompt, max_tokens=max_tokens)
            return {'success': True, 'response': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ==================== STUDENT PERFORMANCE ANALYSIS ====================
    
    def analyze_student_performance(self, student_id: str) -> Dict[str, Any]:
        """
        Comprehensive student performance analysis
        
        Returns:
            {
                'success': bool,
                'analysis': {
                    'avg_score': float,
                    'total_exams': int,
                    'strengths': list,
                    'weaknesses': list,
                    'performance_trend': str,
                    'predicted_next_score': float,
                    'engagement': dict,
                    'recommendations': list
                },
                'error': str
            }
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get exam submissions
            cur.execute("""
                SELECT es.exam_id, es.score, es.max_score, es.submitted_at,
                       e.exam_name, e.subject
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s
                ORDER BY es.submitted_at DESC
                LIMIT 20
            """, (student_id,))
            
            submissions = cur.fetchall()
            
            if not submissions:
                return {
                    'success': True,
                    'analysis': {
                        'avg_score': 0,
                        'total_exams': 0,
                        'strengths': [],
                        'weaknesses': [],
                        'performance_trend': 'no_data',
                        'recommendations': ['Complete your first exam to get analysis']
                    }
                }
            
            # Calculate statistics
            scores = [s['score'] for s in submissions]
            max_scores = [s['max_score'] for s in submissions]
            percentages = [(s/m * 100) if m > 0 else 0 for s, m in zip(scores, max_scores)]
            
            avg_score = sum(scores) / len(scores) if scores else 0
            avg_percentage = sum(percentages) / len(percentages) if percentages else 0
            
            # Performance trend
            if len(percentages) >= 2:
                recent = sum(percentages[-5:]) / len(percentages[-5:])
                older = sum(percentages[:-5]) / len(percentages[:-5]) if len(percentages) > 5 else recent
                trend = 'improving' if recent > older else 'declining' if recent < older else 'stable'
            else:
                trend = 'not_enough_data'
            
            # Identify strengths and weaknesses by subject
            cur.execute("""
                SELECT e.subject, AVG(es.score::float / es.max_score * 100) as avg_pct
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s
                GROUP BY e.subject
                ORDER BY avg_pct DESC
            """, (student_id,))
            
            subject_scores = cur.fetchall()
            strengths = [s['subject'] for s in subject_scores[:3] if s['avg_pct'] > 70]
            weaknesses = [s['subject'] for s in subject_scores[-3:] if s['avg_pct'] < 60]
            
            # Engagement metrics
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT CAST(es.submitted_at AS DATE)) as days_active,
                    COUNT(*) as total_submissions,
                    AVG(EXTRACT(EPOCH FROM (es.submitted_at - es.created_at))/60) as avg_time_minutes
                FROM exam_submissions es
                WHERE es.student_id = %s AND es.submitted_at > NOW() - INTERVAL '30 days'
            """, (student_id,))
            
            engagement_data = cur.fetchone()
            engagement = {
                'days_active_30d': engagement_data['days_active'] or 0,
                'submissions_30d': engagement_data['total_submissions'] or 0,
                'avg_time_per_exam_min': round(engagement_data['avg_time_minutes'] or 0, 2)
            }
            
            # Generate AI recommendations
            prompt = f"""
            A student has:
            - Average score: {avg_percentage:.1f}%
            - Performance trend: {trend}
            - Strengths: {', '.join(strengths) if strengths else 'None identified'}
            - Weaknesses: {', '.join(weaknesses) if weaknesses else 'None identified'}
            
            Provide 3 specific, actionable learning recommendations (one sentence each).
            """
            
            ai_response = self._call_model(prompt)
            recommendations = []
            if ai_response['success']:
                lines = ai_response['response'].split('\n')
                recommendations = [line.strip() for line in lines if line.strip()][:3]
            
            # Predict next score using simple linear regression
            if len(percentages) >= 3:
                # Simple trend-based prediction
                recent_avg = sum(percentages[-3:]) / 3
                predicted = min(100, max(0, recent_avg + (recent_avg - avg_percentage) * 0.2))
            else:
                predicted = avg_percentage
            
            # Store analytics in database
            cur.execute("""
                INSERT INTO student_analytics (student_id, avg_score, total_exams, 
                                              performance_trend, predicted_score, 
                                              last_analyzed)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id) DO UPDATE SET
                    avg_score = EXCLUDED.avg_score,
                    total_exams = EXCLUDED.total_exams,
                    performance_trend = EXCLUDED.performance_trend,
                    predicted_score = EXCLUDED.predicted_score,
                    last_analyzed = EXCLUDED.last_analyzed
            """, (student_id, avg_score, len(submissions), trend, predicted, datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'analysis': {
                    'avg_score': round(avg_score, 2),
                    'avg_percentage': round(avg_percentage, 2),
                    'total_exams': len(submissions),
                    'strengths': strengths,
                    'weaknesses': weaknesses,
                    'performance_trend': trend,
                    'predicted_next_score': round(predicted, 2),
                    'engagement': engagement,
                    'recommendations': recommendations
                }
            }
        
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== PLAGIARISM DETECTION ====================
    
    def check_plagiarism(self, submission_id: str, text_content: str, 
                        student_id: str, threshold: float = 0.7) -> Dict[str, Any]:
        """
        Check submission for plagiarism using similarity comparison
        
        Args:
            submission_id: ID of the submission
            text_content: The text to check
            student_id: Student who submitted
            threshold: Similarity threshold to flag plagiarism (0-1)
            
        Returns:
            {
                'success': bool,
                'plagiarism_score': float (0-100),
                'matches': list,
                'is_plagiarized': bool,
                'error': str
            }
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all previous submissions from other students
            cur.execute("""
                SELECT es.id, es.student_id, es.essay_answer FROM exam_submissions es
                WHERE es.essay_answer IS NOT NULL 
                AND es.student_id != %s
                ORDER BY es.submitted_at DESC
                LIMIT 50
            """, (student_id,))
            
            previous_submissions = cur.fetchall()
            
            max_similarity = 0
            matching_submissions = []
            
            # Compare with each previous submission
            for prev in previous_submissions:
                similarity = self._calculate_similarity(text_content, prev['essay_answer'])
                if similarity > max_similarity:
                    max_similarity = similarity
                
                if similarity >= threshold:
                    matching_submissions.append({
                        'submission_id': prev['id'],
                        'student_id': prev['student_id'],
                        'similarity': round(similarity * 100, 2)
                    })
            
            plagiarism_score = max_similarity * 100
            is_plagiarized = plagiarism_score >= (threshold * 100)
            
            # Store plagiarism check result
            cur.execute("""
                INSERT INTO plagiarism_checks (submission_id, student_id, plagiarism_score,
                                             is_flagged, checked_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (submission_id, student_id, plagiarism_score, is_plagiarized, datetime.utcnow()))
            
            # Flag suspicious submission
            if is_plagiarized:
                cur.execute("""
                    INSERT INTO audit_logs (user_id, action, details, timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (student_id, 'PLAGIARISM_DETECTED', 
                     f'Plagiarism score: {plagiarism_score:.1f}%', datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'plagiarism_score': round(plagiarism_score, 2),
                'is_plagiarized': is_plagiarized,
                'matches': matching_submissions,
                'threshold': threshold * 100
            }
        
        except Exception as e:
            logger.error(f"Plagiarism check error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using SequenceMatcher
        
        Returns:
            float: Similarity ratio (0-1)
        """
        try:
            matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
            return matcher.ratio()
        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0

    # ==================== LEARNING RECOMMENDATIONS ====================
    
    def get_learning_recommendations(self, student_id: str) -> Dict[str, Any]:
        """
        Get personalized learning recommendations based on performance
        
        Returns:
            {
                'success': bool,
                'recommendations': [
                    {'type': str, 'resource': str, 'reason': str, 'priority': str}
                ],
                'error': str
            }
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get student's weak subjects
            cur.execute("""
                SELECT e.subject, AVG(es.score::float / es.max_score * 100) as avg_pct
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s
                GROUP BY e.subject
                HAVING AVG(es.score::float / es.max_score * 100) < 70
                ORDER BY avg_pct ASC
                LIMIT 3
            """, (student_id,))
            
            weak_subjects = cur.fetchall()
            recommendations = []
            
            # Recommend study documents for weak subjects
            for subject_data in weak_subjects:
                subject = subject_data['subject']
                
                # Find relevant documents
                cur.execute("""
                    SELECT id, document_name FROM documents
                    WHERE subject = %s AND is_premium = false
                    LIMIT 5
                """, (subject,))
                
                docs = cur.fetchall()
                for doc in docs:
                    recommendations.append({
                        'type': 'study_material',
                        'resource': doc['document_name'],
                        'resource_id': doc['id'],
                        'subject': subject,
                        'reason': f'Improve {subject} (currently below 70%)',
                        'priority': 'high'
                    })
                
                # Find practice exams
                cur.execute("""
                    SELECT id, exam_name FROM exams
                    WHERE subject = %s AND exam_type = 'practice'
                    ORDER BY difficulty DESC
                    LIMIT 3
                """, (subject,))
                
                exams = cur.fetchall()
                for exam in exams:
                    recommendations.append({
                        'type': 'practice_exam',
                        'resource': exam['exam_name'],
                        'resource_id': exam['id'],
                        'subject': subject,
                        'reason': f'Practice {subject} skills',
                        'priority': 'high'
                    })
            
            # Recommend videos for strong subjects (reinforcement)
            cur.execute("""
                SELECT e.subject, AVG(es.score::float / es.max_score * 100) as avg_pct
                FROM exam_submissions es
                JOIN exams e ON es.exam_id = e.id
                WHERE es.student_id = %s
                GROUP BY e.subject
                HAVING AVG(es.score::float / es.max_score * 100) >= 80
                ORDER BY avg_pct DESC
                LIMIT 2
            """, (student_id,))
            
            strong_subjects = cur.fetchall()
            
            for subject_data in strong_subjects:
                subject = subject_data['subject']
                
                cur.execute("""
                    SELECT id, video_title FROM videos
                    WHERE subject = %s AND video_type = 'advanced'
                    LIMIT 2
                """, (subject,))
                
                videos = cur.fetchall()
                for video in videos:
                    recommendations.append({
                        'type': 'advanced_video',
                        'resource': video['video_title'],
                        'resource_id': video['id'],
                        'subject': subject,
                        'reason': f'Advanced {subject} concepts',
                        'priority': 'medium'
                    })
            
            return {
                'success': True,
                'recommendations': recommendations
            }
        
        except Exception as e:
            logger.error(f"Recommendations error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== SYSTEM HEALTH MONITORING ====================
    
    def record_system_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record system health metrics
        
        Args:
            metrics: {
                'cpu_usage': float,
                'memory_usage': float,
                'active_users': int,
                'api_response_time_ms': float,
                'db_connection_pool_usage': float
            }
            
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO system_health_metrics (cpu_usage, memory_usage, active_users,
                                                  api_response_time_ms, db_pool_usage,
                                                  recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                metrics.get('cpu_usage', 0),
                metrics.get('memory_usage', 0),
                metrics.get('active_users', 0),
                metrics.get('api_response_time_ms', 0),
                metrics.get('db_connection_pool_usage', 0),
                datetime.utcnow()
            ))
            
            conn.commit()
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Health recording error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get recent system health data
        
        Returns:
            {'success': bool, 'health': dict, 'status': str, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT cpu_usage, memory_usage, active_users, api_response_time_ms,
                       db_pool_usage, recorded_at
                FROM system_health_metrics
                ORDER BY recorded_at DESC
                LIMIT 1
            """)
            
            latest = cur.fetchone()
            
            if not latest:
                return {
                    'success': True,
                    'health': {'status': 'no_data'},
                    'status': 'unknown'
                }
            
            # Determine overall health status
            status = 'healthy'
            if latest['cpu_usage'] > 80 or latest['memory_usage'] > 85:
                status = 'warning'
            if latest['cpu_usage'] > 95 or latest['memory_usage'] > 95:
                status = 'critical'
            if latest['api_response_time_ms'] > 1000:
                status = 'critical'
            
            return {
                'success': True,
                'health': {
                    'cpu_usage': latest['cpu_usage'],
                    'memory_usage': latest['memory_usage'],
                    'active_users': latest['active_users'],
                    'api_response_time_ms': latest['api_response_time_ms'],
                    'db_pool_usage': latest['db_pool_usage'],
                    'recorded_at': latest['recorded_at'].isoformat()
                },
                'status': status
            }
        
        except Exception as e:
            logger.error(f"Health retrieval error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
