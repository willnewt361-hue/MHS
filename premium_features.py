"""
Premium Features Analytics and Gamification Module
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict

class AnalyticsService:
    """Performance analytics and reporting"""
    
    @staticmethod
    def calculate_performance_metrics(quiz_scores: List[Dict]) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not quiz_scores:
            return {"average": 0, "trend": "stable", "consistency": 0}
        
        scores = [s.get('score', 0) for s in quiz_scores]
        avg = sum(scores) / len(scores) if scores else 0
        
        # Calculate trend (improving, declining, stable)
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:-3]) / (len(scores) - 3) if len(scores) > 3 else avg
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate consistency (standard deviation)
        if scores:
            variance = sum((x - avg) ** 2 for x in scores) / len(scores)
            consistency = 100 - min(100, (variance ** 0.5))
        else:
            consistency = 0
        
        return {
            "average": round(avg, 2),
            "trend": trend,
            "consistency": round(consistency, 2),
            "total_attempts": len(scores),
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0
        }
    
    @staticmethod
    def generate_progress_report(student_data: Dict) -> Dict:
        """Generate detailed progress report"""
        return {
            "student_id": student_data.get('id'),
            "generated_at": datetime.now().isoformat(),
            "overall_performance": student_data.get('overall_score', 0),
            "subjects": student_data.get('subjects', {}),
            "strengths": student_data.get('strengths', []),
            "areas_for_improvement": student_data.get('weaknesses', []),
            "study_consistency": student_data.get('consistency_score', 0),
            "recommendation": "Student is making good progress. Continue current study routine."
        }

class GamificationService:
    """Gamification engine for motivation"""
    
    BADGES = {
        "first_quiz": {"name": "Quiz Starter", "icon": "🎯", "points": 10},
        "perfect_score": {"name": "Perfect Score", "icon": "⭐", "points": 50},
        "streak_7": {"name": "Week Warrior", "icon": "🔥", "points": 30},
        "streak_30": {"name": "Month Master", "icon": "👑", "points": 100},
        "100_questions": {"name": "Hundred Questions", "icon": "💯", "points": 25},
        "high_consistency": {"name": "Consistent Learner", "icon": "📈", "points": 20},
        "weak_to_strong": {"name": "Comeback Kid", "icon": "🚀", "points": 40},
    }
    
    @staticmethod
    def award_badge(student_id: str, badge_key: str) -> Dict:
        """Award a badge to student"""
        badge = GamificationService.BADGES.get(badge_key)
        if not badge:
            return {"success": False, "message": "Badge not found"}
        
        return {
            "success": True,
            "badge": badge_key,
            "badge_name": badge["name"],
            "icon": badge["icon"],
            "points_awarded": badge["points"],
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def calculate_points(action: str, value: float = 1) -> int:
        """Calculate points for actions"""
        points_map = {
            "quiz_complete": 5,
            "perfect_score": 50,
            "study_session_1h": 10,
            "assignment_submit": 15,
            "peer_help": 20,
            "certificate_earned": 100,
            "daily_login": 2
        }
        return points_map.get(action, 0) * int(value)
    
    @staticmethod
    def get_leaderboard(students_data: List[Dict], top_n: int = 10) -> List[Dict]:
        """Generate leaderboard"""
        sorted_students = sorted(
            students_data,
            key=lambda x: x.get('total_points', 0),
            reverse=True
        )
        
        leaderboard = []
        for rank, student in enumerate(sorted_students[:top_n], 1):
            leaderboard.append({
                "rank": rank,
                "student_name": student.get('fullName'),
                "points": student.get('total_points', 0),
                "badges": student.get('badges', []),
                "streak": student.get('streak', 0)
            })
        
        return leaderboard

class AttendanceService:
    """Attendance tracking and analytics"""
    
    @staticmethod
    def calculate_attendance_percentage(attendance_records: List[Dict]) -> float:
        """Calculate attendance percentage"""
        if not attendance_records:
            return 0
        
        present = sum(1 for r in attendance_records if r.get('status') == 'present')
        return round((present / len(attendance_records)) * 100, 2)
    
    @staticmethod
    def get_attendance_trends(records: List[Dict], days: int = 30) -> Dict:
        """Analyze attendance trends"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [r for r in records if datetime.fromisoformat(r.get('date', '')) > cutoff_date]
        
        if not recent_records:
            return {"trend": "no_data", "percentage": 0}
        
        present_count = sum(1 for r in recent_records if r.get('status') == 'present')
        percentage = round((present_count / len(recent_records)) * 100, 2)
        
        return {
            "percentage": percentage,
            "days_present": present_count,
            "days_absent": len(recent_records) - present_count,
            "trend": "good" if percentage >= 80 else "needs_improvement" if percentage >= 70 else "critical"
        }

class ReportGenerationService:
    """Generate comprehensive reports"""
    
    @staticmethod
    def generate_student_report(student_id: str, data: Dict) -> Dict:
        """Generate comprehensive student report"""
        return {
            "report_type": "student_comprehensive",
            "student_id": student_id,
            "student_name": data.get('fullName'),
            "generated_at": datetime.now().isoformat(),
            "academic_performance": {
                "overall_score": data.get('overall_score', 0),
                "subjects": data.get('subjects', {}),
                "gpa": data.get('gpa', 0)
            },
            "attendance": {
                "percentage": data.get('attendance_percentage', 0),
                "status": "good" if data.get('attendance_percentage', 0) >= 80 else "needs_attention"
            },
            "progress": {
                "improvement": data.get('improvement_trend', 'stable'),
                "consistency": data.get('consistency', 0)
            },
            "recommendations": data.get('recommendations', []),
            "conclusion": f"Student is performing {'excellently' if data.get('overall_score', 0) >= 80 else 'well' if data.get('overall_score', 0) >= 70 else 'adequately' if data.get('overall_score', 0) >= 60 else 'below expectations'}. Continue current study schedule."
        }
    
    @staticmethod
    def generate_class_report(class_name: str, students_data: List[Dict]) -> Dict:
        """Generate class-level report"""
        if not students_data:
            return {"class": class_name, "students_count": 0, "data": {}}
        
        scores = [s.get('overall_score', 0) for s in students_data]
        class_avg = sum(scores) / len(scores) if scores else 0
        
        return {
            "class": class_name,
            "generated_at": datetime.now().isoformat(),
            "students_count": len(students_data),
            "class_average": round(class_avg, 2),
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "pass_rate": round(sum(1 for s in scores if s >= 60) / len(scores) * 100, 2) if scores else 0,
            "top_performers": sorted(students_data, key=lambda x: x.get('overall_score', 0), reverse=True)[:5],
            "students_needing_support": sorted(students_data, key=lambda x: x.get('overall_score', 0))[:5]
        }

analytics_service = AnalyticsService()
gamification_service = GamificationService()
attendance_service = AttendanceService()
report_service = ReportGenerationService()
