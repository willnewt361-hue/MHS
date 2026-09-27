"""
Advanced Exam Predictor with Machine Learning
Uses heuristics + AI to predict exam topics and difficulty
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict

class ExamPredictorML:
    """ML-based exam question predictor"""
    
    def __init__(self):
        self.topic_frequency = defaultdict(int)
        self.difficulty_distribution = defaultdict(list)
        self.student_weak_topics = defaultdict(set)
    
    def train_on_performance(self, performance_data: List[Dict]) -> Dict:
        """Train model on historical performance data"""
        topic_scores = defaultdict(list)
        
        for perf in performance_data:
            subject = perf.get('subject', '')
            score = perf.get('score', 0)
            
            # Track scores per topic
            topic_scores[subject].append(score)
        
        # Calculate averages and identify weak areas
        predictions = {}
        for topic, scores in topic_scores.items():
            avg_score = sum(scores) / len(scores) if scores else 0
            weak = avg_score < 60
            predictions[topic] = {
                'average_score': round(avg_score, 2),
                'weak': weak,
                'attempts': len(scores),
                'trend': 'improving' if scores[-1] > scores[0] else 'declining'
            }
        
        return predictions
    
    def predict_questions(self, student_id: str, subject: str, performance_history: List[Dict]) -> Dict:
        """Predict likely exam questions based on patterns"""
        
        # Analyze performance patterns
        weak_topics = []
        strong_topics = []
        
        for perf in performance_history:
            score = perf.get('score', 0)
            if score < 60:
                weak_topics.append(perf.get('subject', subject))
            elif score >= 80:
                strong_topics.append(perf.get('subject', subject))
        
        # Predict difficulty distribution
        avg_score = sum([p.get('score', 0) for p in performance_history]) / len(performance_history) if performance_history else 0
        
        if avg_score >= 80:
            difficulty_dist = {'easy': 0.2, 'medium': 0.3, 'hard': 0.5}
        elif avg_score >= 60:
            difficulty_dist = {'easy': 0.3, 'medium': 0.5, 'hard': 0.2}
        else:
            difficulty_dist = {'easy': 0.5, 'medium': 0.3, 'hard': 0.2}
        
        # Common question types in exams
        question_types = [
            'Multiple Choice (40%)',
            'Short Answer (30%)',
            'Essay (20%)',
            'Problem Solving (10%)'
        ]
        
        # Predicted topics
        predicted_topics = list(set(weak_topics))[:5]  # Top 5 weak areas
        if not predicted_topics:
            predicted_topics = [subject]
        
        return {
            'predicted_topics': predicted_topics,
            'question_types': question_types,
            'difficulty_distribution': difficulty_dist,
            'preparation_focus': f"Focus on {', '.join(predicted_topics[:2])}",
            'estimated_pass_probability': min(100, max(30, avg_score + 15)),
            'time_to_prepare_hours': 20 if avg_score < 60 else 10 if avg_score < 75 else 5
        }
    
    def recommend_study_focus(self, performance_data: List[Dict]) -> List[str]:
        """Recommend what student should focus on"""
        weak_areas = [p.get('subject') for p in performance_data if p.get('score', 0) < 60]
        recommendations = []
        
        if weak_areas:
            top_weak = Counter(weak_areas).most_common(3)
            for area, count in top_weak:
                recommendations.append(f"Focus on {area} ({count} weak attempts)")
        
        if len(performance_data) > 0:
            recent_avg = sum([p.get('score', 0) for p in performance_data[-3:]]) / min(3, len(performance_data))
            if recent_avg > 75:
                recommendations.append("Maintain current study pace - performing well!")
            elif recent_avg < 50:
                recommendations.append("Intensive revision needed - seek tutoring support")
        
        return recommendations if recommendations else ["Continue consistent studying"]

exam_predictor_ml = ExamPredictorML()
