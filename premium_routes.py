"""
Premium Features Routes for Mengo-Hub
All premium endpoints and AI integration
"""

from flask import request, jsonify, g
from functools import wraps
import json
from datetime import datetime, timedelta
from email_service import email_service
from ai_service import ai_service
from premium_features import (
    analytics_service, gamification_service,
    attendance_service, report_service
)

def require_auth(f):
    """Require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def register_premium_routes(app, get_db, require_admin_token):
    """Register all premium feature routes"""
    
    # ============= SMART REVISION =============
    @app.route('/api/premium/smart-revision', methods=['POST'])
    @require_auth
    def smart_revision():
        """AI-powered revision based on UNEB patterns"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            subject = data.get('subject')
            difficulty = data.get('difficulty', 'medium')
            
            if not student_id or not subject:
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            db = get_db()
            
            # Get student performance data
            performance = db.execute(
                'SELECT * FROM student_performance WHERE student_id = ? AND subject = ? ORDER BY created_at DESC LIMIT 10',
                (student_id, subject)
            ).fetchall()
            
            # Generate AI-powered questions
            ai_questions = ai_service.generate_revision_questions(
                subject=subject,
                difficulty=difficulty,
                count=10,
                context=f"Student performance: {len([p for p in performance if dict(p).get('score', 0) >= 70])} high scores"
            )
            
            # Get existing quiz questions
            quiz_questions = db.execute(
                'SELECT * FROM quiz_questions WHERE subject = ? AND difficulty = ? ORDER BY RANDOM() LIMIT 5',
                (subject, difficulty)
            ).fetchall()
            
            return jsonify({
                'success': True,
                'ai_questions': ai_questions if isinstance(ai_questions, list) else [ai_questions],
                'quiz_questions': [dict(q) for q in quiz_questions],
                'recommendations': [
                    'Focus on exam-style questions',
                    'Practice past papers',
                    'Review weak areas identified above'
                ]
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= WEAKNESS DETECTOR =============
    @app.route('/api/premium/weakness-detector', methods=['GET'])
    @require_auth
    def weakness_detector():
        """Analyze student weaknesses"""
        try:
            student_id = request.args.get('student_id')
            db = get_db()
            
            performance_records = db.execute(
                'SELECT * FROM student_performance WHERE student_id = ? ORDER BY created_at DESC LIMIT 20',
                (student_id,)
            ).fetchall()
            
            if not performance_records:
                return jsonify({'success': True, 'weaknesses': {}})
            
            perf_data = [dict(p) for p in performance_records]
            weaknesses = ai_service.analyze_student_weaknesses({'performance': perf_data})
            
            return jsonify({
                'success': True,
                'weaknesses': weaknesses.get('weak_subjects', []),
                'recommendations': weaknesses.get('recommendations', []),
                'focus_areas': weaknesses.get('focus_areas', []),
                'estimated_improvement_time': weaknesses.get('estimated_improvement_time', '4 weeks')
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= EXAM PREDICTOR =============
    @app.route('/api/premium/exam-predictor', methods=['GET'])
    @require_auth
    def exam_predictor():
        """Predict likely exam questions"""
        try:
            student_id = request.args.get('student_id')
            subject = request.args.get('subject')
            db = get_db()
            
            past_performance = db.execute(
                'SELECT * FROM student_performance WHERE student_id = ? AND subject = ? ORDER BY created_at DESC LIMIT 5',
                (student_id, subject)
            ).fetchall()
            
            if not past_performance:
                return jsonify({'success': False, 'message': 'No performance data'}), 404
            
            perf_list = [dict(p) for p in past_performance]
            predictions = ai_service.predict_exam_questions(student_id, subject, perf_list)
            
            return jsonify({
                'success': True,
                'predicted_topics': predictions.get('predicted_topics', []),
                'question_types': predictions.get('question_types', []),
                'difficulty_distribution': predictions.get('difficulty_distribution', {}),
                'preparation_focus': predictions.get('preparation_focus', '')
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= PERSONALIZED STUDY PLANS =============
    @app.route('/api/premium/study-plan', methods=['POST', 'GET'])
    @require_auth
    def study_plan():
        """Generate AI-powered study plans"""
        try:
            if request.method == 'GET':
                student_id = request.args.get('student_id')
                db = get_db()
                plans = db.execute(
                    'SELECT * FROM study_plans WHERE student_id = ? ORDER BY created_at DESC LIMIT 5',
                    (student_id,)
                ).fetchall()
                
                return jsonify({
                    'success': True,
                    'plans': [{'id': dict(p).get('id'), 'data': json.loads(dict(p).get('plan_data', '{}'))} for p in plans]
                })
            else:
                data = request.get_json() or {}
                student_id = data.get('student_id')
                weaknesses = data.get('weaknesses', [])
                hours_per_day = data.get('hours_per_day', 2)
                
                plan = ai_service.generate_study_plan(student_id, weaknesses, hours_per_day)
                
                db = get_db()
                db.execute(
                    'INSERT INTO study_plans (student_id, plan_data, ai_generated) VALUES (?, ?, ?)',
                    (student_id, json.dumps(plan), 1)
                )
                db.commit()
                
                return jsonify({'success': True, 'study_plan': plan})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= ENHANCED QUIZ =============
    @app.route('/api/premium/quiz', methods=['GET', 'POST'])
    @require_auth
    def premium_quiz():
        """Interactive quiz with explanations and scoring"""
        try:
            if request.method == 'GET':
                subject = request.args.get('subject')
                difficulty = request.args.get('difficulty', 'medium')
                count = int(request.args.get('count', 10))
                
                db = get_db()
                questions = db.execute(
                    'SELECT id, question, options, correct_answer, explanation, difficulty FROM quiz_questions WHERE subject = ? AND difficulty = ? ORDER BY RANDOM() LIMIT ?',
                    (subject, difficulty, count)
                ).fetchall()
                
                return jsonify({
                    'success': True,
                    'quiz': [dict(q) for q in questions],
                    'count': len(list(questions))
                })
            else:
                data = request.get_json() or {}
                student_id = data.get('student_id')
                subject = data.get('subject')
                answers = data.get('answers', [])
                
                score = sum(1 for ans in answers if ans.get('correct'))
                total = len(answers)
                percentage = (score / total * 100) if total > 0 else 0
                
                db = get_db()
                db.execute(
                    'INSERT INTO student_performance (student_id, subject, score, total_questions, created_at) VALUES (?, ?, ?, ?, ?)',
                    (student_id, subject, percentage, total, datetime.now().isoformat())
                )
                db.commit()
                
                # Award points for completion
                gamification_service.award_badge(student_id, 'first_quiz')
                if percentage == 100:
                    gamification_service.award_badge(student_id, 'perfect_score')
                
                return jsonify({
                    'success': True,
                    'score': score,
                    'total': total,
                    'percentage': round(percentage, 2),
                    'feedback': 'Excellent!' if percentage >= 80 else 'Good effort' if percentage >= 60 else 'Keep practicing'
                })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= ANALYTICS =============
    @app.route('/api/premium/analytics/<student_id>', methods=['GET'])
    @require_auth
    def get_analytics(student_id):
        """Get comprehensive student analytics"""
        try:
            db = get_db()
            
            # Get performance data
            performance = db.execute(
                'SELECT * FROM student_performance WHERE student_id = ? ORDER BY created_at DESC LIMIT 50',
                (student_id,)
            ).fetchall()
            
            perf_list = [dict(p) for p in performance]
            metrics = analytics_service.calculate_performance_metrics(perf_list)
            
            # Get attendance
            attendance = db.execute(
                'SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC LIMIT 30',
                (student_id,)
            ).fetchall()
            
            attend_list = [dict(a) for a in attendance]
            attendance_pct = attendance_service.calculate_attendance_percentage(attend_list)
            
            return jsonify({
                'success': True,
                'performance_metrics': metrics,
                'attendance_percentage': attendance_pct,
                'subjects': list(set([p.get('subject') for p in perf_list if p.get('subject')]))
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= ATTENDANCE TRACKING =============
    @app.route('/api/premium/attendance', methods=['GET', 'POST'])
    @require_admin_token
    def manage_attendance():
        """Manage student attendance"""
        try:
            if request.method == 'GET':
                student_id = request.args.get('student_id')
                db = get_db()
                
                records = db.execute(
                    'SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC LIMIT 30',
                    (student_id,)
                ).fetchall()
                
                return jsonify({'success': True, 'records': [dict(r) for r in records]})
            else:
                data = request.get_json() or {}
                student_id = data.get('student_id')
                date = data.get('date', datetime.now().date().isoformat())
                status = data.get('status', 'present')
                
                db = get_db()
                db.execute(
                    'INSERT OR REPLACE INTO attendance (student_id, date, status) VALUES (?, ?, ?)',
                    (student_id, date, status)
                )
                db.commit()
                
                return jsonify({'success': True, 'message': 'Attendance recorded'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= GAMIFICATION =============
    @app.route('/api/premium/gamification/<student_id>', methods=['GET'])
    @require_auth
    def get_gamification(student_id):
        """Get student gamification stats"""
        try:
            db = get_db()
            
            # Get points
            points_records = db.execute(
                'SELECT * FROM student_points WHERE student_id = ? ORDER BY created_at DESC',
                (student_id,)
            ).fetchall()
            
            total_points = sum([dict(p).get('points', 0) for p in points_records])
            
            # Get badges
            badges = db.execute(
                'SELECT badge_name, badge_key FROM student_badges WHERE student_id = ?',
                (student_id,)
            ).fetchall()
            
            return jsonify({
                'success': True,
                'total_points': total_points,
                'badges': [dict(b) for b in badges],
                'leaderboard_position': 1
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= PAST PAPERS =============
    @app.route('/api/premium/past-papers', methods=['GET', 'POST'])
    @require_auth
    def manage_past_papers():
        """Interactive past papers practice"""
        try:
            if request.method == 'GET':
                subject = request.args.get('subject')
                db = get_db()
                
                papers = db.execute(
                    'SELECT * FROM past_papers WHERE subject = ? ORDER BY year DESC',
                    (subject,)
                ).fetchall()
                
                return jsonify({'success': True, 'papers': [dict(p) for p in papers]})
            else:
                data = request.get_json() or {}
                student_id = data.get('student_id')
                paper_id = data.get('paper_id')
                score = data.get('score')
                total_score = data.get('total_score')
                duration_minutes = data.get('duration_minutes')
                
                db = get_db()
                db.execute(
                    'INSERT INTO past_paper_attempts (student_id, paper_id, score, total_score, duration_minutes, completed_at) VALUES (?, ?, ?, ?, ?, ?)',
                    (student_id, paper_id, score, total_score, duration_minutes, datetime.now().isoformat())
                )
                db.commit()
                
                return jsonify({'success': True, 'message': 'Past paper attempt recorded'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= REPORTS =============
    @app.route('/api/premium/reports/<student_id>', methods=['GET'])
    @require_auth
    def get_reports(student_id):
        """Generate comprehensive reports"""
        try:
            db = get_db()
            
            student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
            performance = db.execute(
                'SELECT AVG(score) as avg_score FROM student_performance WHERE student_id = ?',
                (student_id,)
            ).fetchone()
            
            student_data = {
                'id': student_id,
                'fullName': dict(student).get('fullName') if student else 'Unknown',
                'overall_score': dict(performance).get('avg_score', 0) if performance else 0,
                'subjects': {},
                'strengths': [],
                'weaknesses': [],
                'consistency_score': 85
            }
            
            report = report_service.generate_student_report(student_id, student_data)
            
            return jsonify({'success': True, 'report': report})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= SUMMARIZER =============
    @app.route('/api/premium/summarize', methods=['POST'])
    @require_auth
    def summarize_content():
        """AI-powered content summarization"""
        try:
            data = request.get_json() or {}
            content = data.get('content')
            max_length = data.get('max_length', 200)
            
            if not content:
                return jsonify({'success': False, 'message': 'Content required'}), 400
            
            summary = ai_service.summarize_content(content, max_length)
            
            return jsonify({
                'success': True,
                'summary': summary,
                'original_length': len(content),
                'summary_length': len(summary)
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= AI CHAT =============
    @app.route('/api/premium/ai-chat', methods=['POST'])
    @require_auth
    def ai_chat():
        """Chat with AI assistant"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            message = data.get('message')
            context = data.get('context', 'general')
            
            if not message:
                return jsonify({'success': False, 'message': 'Message required'}), 400
            
            # Query AI
            response = ai_service.query(message)
            
            # Store conversation
            db = get_db()
            db.execute(
                'INSERT INTO ai_chat_messages (student_id, message_text, ai_response, ai_provider, created_at) VALUES (?, ?, ?, ?, ?)',
                (student_id, message, response, ai_service.provider, datetime.now().isoformat())
            )
            db.commit()
            
            return jsonify({
                'success': True,
                'message': message,
                'response': response,
                'provider': ai_service.provider
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= EMAIL CONFIGURATION (ADMIN) =============
    @app.route('/api/admin/email-config', methods=['GET', 'POST'])
    @require_admin_token
    def email_configuration():
        """Configure email settings"""
        try:
            if request.method == 'GET':
                db = get_db()
                configs = db.execute(
                    'SELECT * FROM email_configuration ORDER BY updated_at DESC'
                ).fetchall()
                
                return jsonify({
                    'success': True,
                    'configurations': [dict(c) for c in configs]
                })
            else:
                data = request.get_json() or {}
                admin_id = data.get('admin_id', 'A000')
                provider = data.get('provider', 'gmail')
                config = data.get('config', {})
                
                db = get_db()
                db.execute(
                    'INSERT OR REPLACE INTO email_configuration (admin_id, email_provider, smtp_server, smtp_port, sender_email, is_configured, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (admin_id, provider, config.get('smtp_server'), config.get('smtp_port'), config.get('sender_email'), 1, datetime.now().isoformat())
                )
                db.commit()
                
                return jsonify({'success': True, 'message': f'{provider} email configured'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/email-config/test', methods=['POST'])
    @require_admin_token
    def test_email():
        """Send test email"""
        try:
            data = request.get_json() or {}
            to_email = data.get('to_email')
            
            if not to_email:
                return jsonify({'success': False, 'message': 'Email address required'}), 400
            
            result = email_service.send_notification(
                to_email,
                'Test Email from Mengo-Hub',
                'This is a test email to verify email configuration is working correctly.'
            )
            
            return jsonify({
                'success': result,
                'message': 'Test email sent successfully' if result else 'Failed to send test email'
            })
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/admin/send-admin-alert', methods=['POST'])
    @require_admin_token
    def send_admin_alert():
        """Send alert to all admins"""
        try:
            data = request.get_json() or {}
            title = data.get('title')
            message = data.get('message')
            severity = data.get('severity', 'info')
            
            db = get_db()
            admins = db.execute('SELECT email FROM students WHERE is_admin = 1 AND email IS NOT NULL').fetchall()
            admin_emails = [dict(a).get('email') for a in admins if dict(a).get('email')]
            
            if admin_emails:
                email_service.send_admin_alert(admin_emails, title, message, severity)
            
            return jsonify({'success': True, 'admins_notified': len(admin_emails)})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    # ============= CERTIFICATE FIX =============
    @app.route('/api/admin/validate-certificate', methods=['GET'])
    @require_admin_token
    def validate_certificate():
        """Validate admin certificate"""
        try:
            user_id = request.args.get('user_id')
            db = get_db()
            
            user = db.execute('SELECT is_admin, certificate FROM students WHERE id = ?', (user_id,)).fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            is_admin = dict(user).get('is_admin', 0)
            certificate = dict(user).get('certificate')
            
            # Admin is valid if is_admin = 1, certificate field doesn't block access
            if is_admin:
                return jsonify({
                    'success': True,
                    'is_admin': True,
                    'has_certificate': bool(certificate),
                    'message': 'Admin access granted'
                })
            else:
                return jsonify({
                    'success': False,
                    'is_admin': False,
                    'message': 'Admin access denied'
                }), 403
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============= ADMIN PANEL CONTROLS =============
    @app.route('/api/admin/feature-toggles', methods=['GET', 'POST'])
    @require_admin_token
    def feature_toggles():
        """Get or set feature toggles in system_settings"""
        try:
            db = get_db()
            if request.method == 'GET':
                rows = db.execute('SELECT setting_key, setting_value FROM system_settings WHERE setting_key LIKE "feature_%"').fetchall()
                settings = {r['setting_key']: json.loads(r['setting_value']) for r in rows}
                return jsonify({'success': True, 'features': settings})
            else:
                data = request.get_json() or {}
                for key, val in data.items():
                    skey = f'feature_{key}'
                    db.execute('INSERT OR REPLACE INTO system_settings (setting_key, setting_value, updated_at) VALUES (?, ?, ?)',
                               (skey, json.dumps(val), datetime.now().isoformat()))
                db.commit()
                return jsonify({'success': True, 'message': 'Feature toggles updated'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============= ADVANCED EXAM PREDICTOR (AUGMENTED) =============
    @app.route('/api/premium/exam-predictor/advanced', methods=['POST'])
    @require_auth
    def exam_predictor_advanced():
        """Combine simple heuristics with AI predictions to return ranked topics"""
        try:
            data = request.get_json() or {}
            student_id = data.get('student_id')
            subject = data.get('subject')
            past_n = int(data.get('past_n', 10))
            db = get_db()

            perf = db.execute('SELECT subject, score FROM student_performance WHERE student_id = ? ORDER BY created_at DESC LIMIT ?',
                              (student_id, past_n)).fetchall()
            perf_list = [dict(p) for p in perf]

            # Heuristic: topics where scores are lowest in subject range
            # If no detailed topic breakdown, use AI to predict topics
            ai_preds = ai_service.predict_exam_questions(student_id, subject, perf_list)

            # Build combined response
            response = {
                'ai': ai_preds,
                'heuristic': {
                    'recent_scores': perf_list,
                    'advice': ['Focus on weak topics', 'Practice past paper questions']
                }
            }
            return jsonify({'success': True, 'prediction': response})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============= AUDIO STUDY AIDS =============
    @app.route('/api/premium/audio/generate', methods=['POST'])
    @require_auth
    def generate_binaural():
        """Generate binaural beats WAV and return path"""
        try:
            data = request.get_json() or {}
            base_freq = float(data.get('base_freq', 200.0))
            beat_freq = float(data.get('beat_freq', 7.0))
            duration = float(data.get('duration', 120.0))
            sample_rate = int(data.get('sample_rate', 44100))

            import numpy as np
            import wave
            import os

            t = np.linspace(0, duration, int(sample_rate * duration), False)
            left = np.sin(2 * np.pi * base_freq * t)
            right = np.sin(2 * np.pi * (base_freq + beat_freq) * t)

            stereo = np.vstack((left, right)).T
            # Normalize to 16-bit range
            stereo_int = np.int16(stereo * 32767)

            os.makedirs('public/audio/beats', exist_ok=True)
            filename = f"binaural_{int(datetime.now().timestamp())}.wav"
            filepath = os.path.join('public', 'audio', 'beats', filename)

            with wave.open(filepath, 'w') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(stereo_int.tobytes())

            return jsonify({'success': True, 'file': f'audio/beats/{filename}'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============= 3D VISUALIZATION HOOKS =============
    @app.route('/api/premium/3d/models', methods=['GET', 'POST'])
    @require_auth
    def manage_3d_models():
        """Register or list 3D model metadata for front-end to load (Three.js)"""
        try:
            db = get_db()
            if request.method == 'GET':
                row = db.execute('SELECT setting_value FROM system_settings WHERE setting_key = ?', ('3d_models',)).fetchone()
                models = json.loads(row['setting_value']) if row and row['setting_value'] else []
                return jsonify({'success': True, 'models': models})
            else:
                data = request.get_json() or {}
                models = data.get('models', [])
                db.execute('INSERT OR REPLACE INTO system_settings (setting_key, setting_value, updated_at) VALUES (?, ?, ?)',
                           ('3d_models', json.dumps(models), datetime.now().isoformat()))
                db.commit()
                return jsonify({'success': True, 'message': '3D models updated'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/api/premium/3d/model/<model_id>', methods=['GET'])
    @require_auth
    def get_3d_model(model_id):
        """Retrieve specific 3D model metadata"""
        try:
            db = get_db()
            row = db.execute('SELECT setting_value FROM system_settings WHERE setting_key = ?', ('3d_models',)).fetchone()
            models = json.loads(row['setting_value']) if row and row['setting_value'] else []
            for m in models:
                if str(m.get('id')) == str(model_id):
                    return jsonify({'success': True, 'model': m})
            return jsonify({'success': False, 'message': 'Model not found'}), 404
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # ============= ROLE-BASED DASHBOARDS =============
    @app.route('/admin/role/<role>')
    @require_admin_token
    def admin_role_dashboard(role):
    # load role metrics
        metrics = get_role_metrics(role)
        return render_template('admin_role.html', role=role, metrics=metrics)


    @app.route('/api/admin/notes/upload', methods=['POST'])
    @require_admin_token
    def upload_notes():
        f = request.files['file']
        subject = request.form.get('subject')
        level = request.form.get('level')
        filename = secure_filename(f.filename)
        path = os.path.join('public', 'uploads', 'notes', filename)
        f.save(path)
    # insert metadata into DB
        db = get_db(); db.execute('INSERT INTO notes(...) VALUES(...)')
        return jsonify(success=True, url='/uploads/notes/'+filename)

    # ============= N8N WORKFLOW WEBHOOK =============
    @app.route('/webhooks/n8n/mengo', methods=['POST'])
    def n8n_webhook():
        """Basic webhook endpoint for N8N workflows integration - actions: send_admin_alert, create_assignment"""
        try:
            payload = request.get_json() or {}
            action = payload.get('action')
            data = payload.get('data', {})

            if action == 'send_admin_alert':
                title = data.get('title', 'N8N Alert')
                message = data.get('message', '')
                severity = data.get('severity', 'info')
                db = get_db()
                admins = db.execute('SELECT email FROM students WHERE is_admin = 1 AND email IS NOT NULL').fetchall()
                admin_emails = [dict(a).get('email') for a in admins if dict(a).get('email')]
                if admin_emails:
                    email_service.send_admin_alert(admin_emails, title, message, severity)
                return jsonify({'success': True, 'notified': len(admin_emails)})

            if action == 'create_assignment':
                teacher_id = data.get('teacher_id')
                subject = data.get('subject')
                title = data.get('title')
                description = data.get('description')
                stream = data.get('stream')
                klass = data.get('class')
                if not all([teacher_id, subject, title, description]):
                    return jsonify({'success': False, 'message': 'Missing assignment fields'}), 400
                db = get_db()
                db.execute('INSERT INTO assignments (teacher_id, teacher_name, stream, class, subject, title, description) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (teacher_id, data.get('teacher_name',''), stream, klass, subject, title, description))
                db.commit()
                return jsonify({'success': True, 'message': 'Assignment created via N8N webhook'})

            return jsonify({'success': False, 'message': 'Unknown action'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500

    # End of register_premium_routes
