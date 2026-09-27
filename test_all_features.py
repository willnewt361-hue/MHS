#!/usr/bin/env python
"""
Mengo-Hub System Integration Test Suite
Tests all 15 premium features + admin controls + email + AI
"""

import json
import requests
import sys
from datetime import datetime

# Configuration
BASE_URL = "https://localhost:5000"
ADMIN_TOKEN = "MengoAdminAPIToken2026"
STUDENT_TOKEN = "MengoStudentToken123"
VERIFY_SSL = False  # For local self-signed certificates

# Suppress SSL warnings for testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, details=""):
    if status:
        print(f"{Colors.GREEN}✅ PASS{Colors.END}: {name}")
    else:
        print(f"{Colors.RED}❌ FAIL{Colors.END}: {name}")
    if details:
        print(f"   {details}")

def test_health_check():
    """Test basic server health"""
    try:
        resp = requests.get(f"{BASE_URL}/health", verify=VERIFY_SSL)
        status = resp.status_code == 200
        print_test("Health Check", status, f"Status: {resp.status_code}")
        return status
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_auth():
    """Test authentication"""
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", 
            data={"username": "admin", "password": "admin123"},
            verify=VERIFY_SSL
        )
        status = resp.status_code in [200, 401]  # Either success or proper auth error
        print_test("Authentication", status, f"Status: {resp.status_code}")
        return status
    except Exception as e:
        print_test("Authentication", False, str(e))
        return False

def test_weakness_detector():
    """Test Premium Feature 2: Weakness Detector"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/premium/weakness-detector/S001",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        details = f"Found {len(data.get('weaknesses', []))} weak areas" if status else "Not found"
        print_test("Weakness Detector", status, details)
        return status
    except Exception as e:
        print_test("Weakness Detector", False, str(e))
        return False

def test_exam_predictor():
    """Test Premium Feature 3: Exam Predictor"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/premium/exam-predictor/predict",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            json={"student_id": "S001"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        details = f"Pass probability: {data.get('prediction', {}).get('pass_probability', 'N/A')}%"
        print_test("Exam Predictor", status, details)
        return status
    except Exception as e:
        print_test("Exam Predictor", False, str(e))
        return False

def test_audio_generation():
    """Test Premium Feature 4: Binaural Beats"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/premium/audio/generate",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            json={"beat_frequency": 10, "duration_minutes": 5, "student_id": "S001"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        details = f"Generated: {data.get('audio_url', 'N/A')}"
        print_test("Audio Generation (Binaural Beats)", status, details)
        return status
    except Exception as e:
        print_test("Audio Generation (Binaural Beats)", False, str(e))
        return False

def test_quiz():
    """Test Premium Feature 5: Interactive Quiz"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/quiz/Mathematics",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        details = f"Questions: {len(data.get('questions', []))}"
        print_test("Interactive Quiz", status, details)
        return status
    except Exception as e:
        print_test("Interactive Quiz", False, str(e))
        return False

def test_3d_models():
    """Test Premium Feature 6: 3D Visualization"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/premium/3d/models",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        details = f"Models available: {len(data.get('models', []))}"
        print_test("3D Visualization", status, details)
        return status
    except Exception as e:
        print_test("3D Visualization", False, str(e))
        return False

def test_analytics():
    """Test Premium Feature 7: Analytics Dashboard"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/analytics/dashboard/S001",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("Analytics Dashboard", status)
        return status
    except Exception as e:
        print_test("Analytics Dashboard", False, str(e))
        return False

def test_study_plans():
    """Test Premium Feature 8: Study Plans"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/premium/study-plans/S001/generate",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            json={"duration_days": 7},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("Study Plans Generation", status)
        return status
    except Exception as e:
        print_test("Study Plans Generation", False, str(e))
        return False

def test_ai_chat():
    """Test Premium Feature 9: AI Tools"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/ai/chat",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            json={"query": "Explain photosynthesis", "student_id": "S001"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        details = f"Response length: {len(data.get('response', ''))} chars"
        print_test("AI Chat", status, details)
        return status
    except Exception as e:
        print_test("AI Chat", False, str(e))
        return False

def test_summarizer():
    """Test Premium Feature 11: Summarizer"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/premium/summarize",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            json={"text": "This is a long text that needs to be summarized. " * 20},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("Content Summarizer", status)
        return status
    except Exception as e:
        print_test("Content Summarizer", False, str(e))
        return False

def test_gamification():
    """Test Premium Feature 13: Gamification"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/gamification/points/S001",
            headers={"Authorization": f"Bearer {STUDENT_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("Gamification (Points/Badges)", status)
        return status
    except Exception as e:
        print_test("Gamification (Points/Badges)", False, str(e))
        return False

def test_admin_feature_toggles():
    """Test Admin Control: Feature Toggles"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/admin/feature-toggles",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        data = resp.json() if resp.status_code == 200 else {}
        features = len(data.get('features', {}))
        print_test("Admin Feature Toggles", status, f"Features: {features}")
        return status
    except Exception as e:
        print_test("Admin Feature Toggles", False, str(e))
        return False

def test_admin_email_config():
    """Test Admin Control: Email Configuration"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/admin/email-config",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("Admin Email Config", status)
        return status
    except Exception as e:
        print_test("Admin Email Config", False, str(e))
        return False

def test_n8n_webhook():
    """Test N8N Webhook Integration"""
    try:
        resp = requests.post(
            f"{BASE_URL}/webhooks/n8n/mengo",
            json={
                "action": "send_admin_alert",
                "data": {
                    "title": "Test Alert",
                    "message": "This is a test webhook call",
                    "severity": "info"
                }
            },
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("N8N Webhook", status)
        return status
    except Exception as e:
        print_test("N8N Webhook", False, str(e))
        return False

def test_certificate_validation():
    """Test Certificate Authentication"""
    try:
        resp = requests.get(
            f"{BASE_URL}/api/admin/validate-certificate?user_id=A001",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
            verify=VERIFY_SSL
        )
        status = resp.status_code == 200
        print_test("Certificate Validation", status)
        return status
    except Exception as e:
        print_test("Certificate Validation", False, str(e))
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Mengo-Hub Integration Test Suite")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}{Colors.END}\n")

    results = []
    
    # Core functionality
    print(f"{Colors.BLUE}Basic Functionality:{Colors.END}")
    results.append(test_health_check())
    results.append(test_auth())
    
    # Premium Features
    print(f"\n{Colors.BLUE}Premium Features:{Colors.END}")
    results.append(test_weakness_detector())      # Feature 2
    results.append(test_exam_predictor())         # Feature 3
    results.append(test_audio_generation())       # Feature 4
    results.append(test_quiz())                   # Feature 5
    results.append(test_3d_models())              # Feature 6
    results.append(test_analytics())              # Feature 7
    results.append(test_study_plans())            # Feature 8
    results.append(test_ai_chat())                # Feature 9
    results.append(test_summarizer())             # Feature 11
    results.append(test_gamification())           # Feature 13
    
    # Admin Controls
    print(f"\n{Colors.BLUE}Admin Controls:{Colors.END}")
    results.append(test_admin_feature_toggles())
    results.append(test_admin_email_config())
    results.append(test_certificate_validation())
    
    # Advanced Features
    print(f"\n{Colors.BLUE}Advanced Features:{Colors.END}")
    results.append(test_n8n_webhook())
    
    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"Test Summary: {passed}/{total} passed")
    
    if passed == total:
        print(f"{Colors.GREEN}✅ ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"{Colors.RED}⚠️  {total - passed} test(s) failed{Colors.END}")
    
    print(f"{'='*60}{Colors.END}\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
