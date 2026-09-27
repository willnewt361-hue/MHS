"""
WebSocket AI Integration for Mengo-Hub
Real-time AI research, chat, and collaboration
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import json
from ai_service import ai_service

class WebSocketAIManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.setup_handlers()
        self.active_sessions = {}
    
    def setup_handlers(self):
        """Setup all WebSocket event handlers"""
        
        @self.socketio.on('connect', namespace='/ai')
        def handle_connect():
            print(f'Client connected to AI namespace')
            emit('response', {'data': 'Connected to AI Research Engine'})
        
        @self.socketio.on('disconnect', namespace='/ai')
        def handle_disconnect():
            print('Client disconnected from AI')
        
        # ======== AI RESEARCH SESSION ========
        @self.socketio.on('research_start', namespace='/ai')
        def handle_research_start(data):
            """Start a research session"""
            student_id = data.get('student_id')
            topic = data.get('topic')
            subject = data.get('subject')
            
            session_id = f"{student_id}_{datetime.now().timestamp()}"
            self.active_sessions[session_id] = {
                'student_id': student_id,
                'topic': topic,
                'subject': subject,
                'started_at': datetime.now().isoformat(),
                'messages': []
            }
            
            emit('research_started', {
                'session_id': session_id,
                'topic': topic,
                'subject': subject,
                'message': f'Research session started on {topic}'
            })
        
        # ======== AI QUERY ========
        @self.socketio.on('ai_query', namespace='/ai')
        def handle_ai_query(data):
            """Send query to AI and stream response"""
            session_id = data.get('session_id')
            query = data.get('query')
            
            if not session_id or not query:
                emit('error', {'message': 'Session ID and query required'})
                return
            
            session = self.active_sessions.get(session_id)
            if not session:
                emit('error', {'message': 'Session not found'})
                return
            
            # Get AI response
            response = ai_service.query(query)
            
            # Stream response
            emit('ai_response', {
                'session_id': session_id,
                'query': query,
                'response': response,
                'provider': ai_service.provider,
                'timestamp': datetime.now().isoformat()
            })
            
            # Store in session
            session['messages'].append({
                'type': 'query',
                'content': query,
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
        
        # ======== RESEARCH TOPIC ========
        @self.socketio.on('research_topic', namespace='/ai')
        def handle_research_topic(data):
            """Research a specific topic"""
            session_id = data.get('session_id')
            topic = data.get('topic')
            depth = data.get('depth', 'moderate')
            
            if not topic:
                emit('error', {'message': 'Topic required'})
                return
            
            # Research using AI
            research_data = ai_service.research_topic(topic, depth)
            
            emit('research_results', {
                'session_id': session_id,
                'topic': topic,
                'depth': depth,
                'data': research_data,
                'timestamp': datetime.now().isoformat()
            })
        
        # ======== EXPLAIN CONCEPT ========
        @self.socketio.on('explain_concept', namespace='/ai')
        def handle_explain_concept(data):
            """Get detailed explanation for a concept"""
            session_id = data.get('session_id')
            topic = data.get('topic')
            concept = data.get('concept')
            level = data.get('level', 'advanced')
            
            if not concept:
                emit('error', {'message': 'Concept required'})
                return
            
            explanation = ai_service.generate_explanation(topic, concept, level)
            
            emit('explanation', {
                'session_id': session_id,
                'topic': topic,
                'concept': concept,
                'level': level,
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            })
        
        # ======== GENERATE QUESTIONS ========
        @self.socketio.on('generate_questions', namespace='/ai')
        def handle_generate_questions(data):
            """Generate exam-style questions"""
            session_id = data.get('session_id')
            subject = data.get('subject')
            topic = data.get('topic')
            difficulty = data.get('difficulty', 'medium')
            count = data.get('count', 5)
            
            questions = ai_service.generate_revision_questions(
                subject=subject,
                difficulty=difficulty,
                count=count,
                context=f"Topic: {topic}"
            )
            
            emit('questions_generated', {
                'session_id': session_id,
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty,
                'questions': questions if isinstance(questions, list) else [questions],
                'timestamp': datetime.now().isoformat()
            })
        
        # ======== ANALYZE PERFORMANCE ========
        @self.socketio.on('analyze_performance', namespace='/ai')
        def handle_analyze_performance(data):
            """Analyze student performance with AI"""
            session_id = data.get('session_id')
            performance_data = data.get('performance_data', {})
            
            weaknesses = ai_service.analyze_student_weaknesses(performance_data)
            
            emit('performance_analysis', {
                'session_id': session_id,
                'analysis': weaknesses,
                'timestamp': datetime.now().isoformat()
            })
        
        # ======== GENERATE STUDY PLAN ========
        @self.socketio.on('generate_study_plan', namespace='/ai')
        def handle_generate_study_plan(data):
            """Generate personalized study plan"""
            session_id = data.get('session_id')
            student_id = data.get('student_id')
            weaknesses = data.get('weaknesses', [])
            hours_per_day = data.get('hours_per_day', 2)
            
            study_plan = ai_service.generate_study_plan(student_id, weaknesses, hours_per_day)
            
            emit('study_plan_generated', {
                'session_id': session_id,
                'student_id': student_id,
                'study_plan': study_plan,
                'timestamp': datetime.now().isoformat()
            })
        
        # ======== RESEARCH END ========
        @self.socketio.on('research_end', namespace='/ai')
        def handle_research_end(data):
            """End research session"""
            session_id = data.get('session_id')
            
            session = self.active_sessions.pop(session_id, None)
            
            if session:
                duration = (datetime.now() - datetime.fromisoformat(session['started_at'])).total_seconds() / 60
                emit('research_ended', {
                    'session_id': session_id,
                    'duration_minutes': round(duration, 2),
                    'message': 'Research session completed',
                    'messages_count': len(session['messages'])
                })
            else:
                emit('error', {'message': 'Session not found'})
        
        # ======== COLLABORATION ========
        @self.socketio.on('join_research_room', namespace='/ai')
        def handle_join_room(data):
            """Join a research collaboration room"""
            room_id = data.get('room_id')
            user_id = data.get('user_id')
            
            join_room(room_id)
            emit('user_joined', {
                'room_id': room_id,
                'user_id': user_id,
                'message': f'User {user_id} joined research room'
            }, room=room_id)
        
        @self.socketio.on('leave_research_room', namespace='/ai')
        def handle_leave_room(data):
            """Leave research collaboration room"""
            room_id = data.get('room_id')
            user_id = data.get('user_id')
            
            leave_room(room_id)
            emit('user_left', {
                'room_id': room_id,
                'user_id': user_id,
                'message': f'User {user_id} left research room'
            }, room=room_id)
        
        # ======== SHARED NOTES ========
        @self.socketio.on('update_shared_notes', namespace='/ai')
        def handle_update_notes(data):
            """Update shared research notes"""
            room_id = data.get('room_id')
            user_id = data.get('user_id')
            notes = data.get('notes')
            
            emit('notes_updated', {
                'room_id': room_id,
                'user_id': user_id,
                'notes': notes,
                'timestamp': datetime.now().isoformat()
            }, room=room_id)

def register_websocket_ai(app, socketio):
    """Register WebSocket AI manager"""
    manager = WebSocketAIManager(socketio)
    return manager
