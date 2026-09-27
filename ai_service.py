"""
AI Service Module for Mengo-Hub
Supports local LLAMA/GPTAll and cloud AI providers
"""

import os
import json
import asyncio
from typing import Optional, List, Dict
from datetime import datetime
import requests

from gpt4all import GPT4All
MODEL_PATH = os.getenv('GPTALL_MODEL_PATH','models')
LOCAL_MODEL = os.getenv('LOCAL_MODEL','Llama-3.2-3B-Instruct-Q4_0.gguf')


class AIService:
    def __init__(self):
        self.provider = os.getenv('AI_PROVIDER', 'local').lower()  # 'local', 'openai', 'anthropic'
        self.local_model = os.getenv('LOCAL_MODEL', 'llama')
        self.local_url = os.getenv('LOCAL_AI_URL', 'http://localhost:8000')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.model_name = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        
    def generate_revision_questions(self, subject: str, difficulty: str, count: int = 10, context: str = None) -> List[Dict]:
        """Generate revision questions using AI based on UNEB patterns"""
        prompt = f"""Generate {count} exam-style questions for {subject} at {difficulty} difficulty level.
        Format as JSON array with fields: question, options (array of 4), correct_answer, explanation, difficulty
        {"Include context: " + context if context else ""}
        Focus on UNEB (Uganda National Examinations Board) patterns and common question types."""
        
        response = self.query(prompt)
        try:
            return json.loads(response)
        except:
            return [{"question": response, "options": [], "correct_answer": "", "explanation": ""}]
    
    def analyze_student_weaknesses(self, performance_data: Dict) -> Dict:
        """Analyze student performance to identify weak areas"""
        prompt = f"""Analyze this student performance data and identify key weaknesses:
        {json.dumps(performance_data, indent=2)}
        
        Return a JSON object with:
        - weak_subjects: list of struggling subjects
        - recommendations: list of improvement strategies
        - focus_areas: specific topics to improve
        - estimated_improvement_time: weeks needed"""
        
        response = self.query(prompt)
        try:
            return json.loads(response)
        except:
            return {"weak_subjects": [], "recommendations": [], "focus_areas": [], "estimated_improvement_time": "4 weeks"}
    
    def predict_exam_questions(self, student_id: str, subject: str, past_performance: List[Dict]) -> Dict:
        """Predict likely exam questions based on patterns"""
        prompt = f"""Based on this student's past performance and UNEB exam patterns, predict likely exam questions:
        Subject: {subject}
        Past Performance: {json.dumps(past_performance, indent=2)}
        
        Return JSON with:
        - predicted_topics: list of likely topics
        - question_types: common question types expected
        - difficulty_distribution: estimated distribution of difficulties
        - preparation_focus: what to prioritize"""
        
        response = self.query(prompt)
        try:
            return json.loads(response)
        except:
            return {"predicted_topics": [], "question_types": [], "difficulty_distribution": {}, "preparation_focus": ""}
    
    def generate_study_plan(self, student_id: str, weaknesses: List[str], available_hours_per_day: float = 2) -> Dict:
        """Generate personalized AI study plan"""
        prompt = f"""Create a personalized study plan for a student with these weaknesses: {', '.join(weaknesses)}
        Available study time: {available_hours_per_day} hours per day
        
        Return JSON with:
        - daily_schedule: array of {{"time": "HH:MM", "subject": "...", "activity": "...", "duration_minutes": N}}
        - weekly_goals: array of specific, measurable goals
        - resources_needed: learning materials and tools
        - revision_schedule: when to review each topic
        - assessment_checkpoints: when to test progress"""
        
        response = self.query(prompt)
        try:
            return json.loads(response)
        except:
            return {"daily_schedule": [], "weekly_goals": [], "resources_needed": [], "revision_schedule": [], "assessment_checkpoints": []}
    
    def summarize_content(self, content: str, max_length: int = 200) -> str:
        """Summarize educational content"""
        prompt = f"""Summarize this educational content in {max_length} words maximum. Keep it clear and useful for studying:
        
        {content}
        
        Provide only the summary, no additional text."""
        
        return self.query(prompt)
    
    def generate_explanation(self, topic: str, concept: str, student_level: str = 'advanced') -> str:
        """Generate detailed explanation for a concept"""
        prompt = f"""Explain '{concept}' in the context of {topic} for a {student_level} level student.
        Include:
        1. Simple definition
        2. Key points
        3. Real-world examples
        4. Common misconceptions to avoid
        5. How it connects to related topics"""
        
        return self.query(prompt)
    
    def research_topic(self, topic: str, depth: str = 'moderate') -> Dict:
        """Research a topic and return structured information"""
        prompt = f"""Research and provide comprehensive information on: {topic}
        Depth level: {depth}
        
        Return JSON with:
        - overview: brief introduction
        - key_points: main ideas
        - subtopics: related areas to explore
        - historical_context: background and evolution
        - current_applications: modern relevance
        - resources: where to learn more"""
        
        response = self.query(prompt)
        try:
            return json.loads(response)
        except:
            return {"overview": "", "key_points": [], "subtopics": [], "historical_context": "", "current_applications": "", "resources": []}
    
    def query(self, prompt: str) -> str:
        """Query AI using configured provider"""
        if self.provider == 'local':
            return self._query_local(prompt)
        elif self.provider == 'openai':
            return self._query_openai(prompt)
        elif self.provider == 'anthropic':
            return self._query_anthropic(prompt)
        else:
            return "AI provider not configured"
    
    def _query_local(self, prompt: str) -> str:
        """Query local LLAMA/GPTAll model"""
        try:
            # Try GPTAll first
            try:
                import gptall
                response = gptall.ask(prompt)
                return response
            except:
                pass
            
            # Fallback to HTTP endpoint
            response = requests.post(
                f"{self.local_url}/api/generate",
                json={"prompt": prompt, "stream": False},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('text', data.get('response', ''))
            else:
                return f"Local AI error: {response.status_code}"
        except Exception as e:
            return f"Error querying local AI: {str(e)}"
    
    def load_local():
        return GPT4All(LOCAL_MODEL, model_path=MODEL_PATH)

    def _query_openai(self, prompt: str) -> str:
        """Query OpenAI API"""
        try:
            import openai
            openai.api_key = self.openai_key
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert educational AI assistant for Mengo-Hub platform."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI error: {str(e)}"
    
    def _query_anthropic(self, prompt: str) -> str:
        """Query Anthropic Claude API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            return f"Anthropic error: {str(e)}"

ai_service = AIService()
