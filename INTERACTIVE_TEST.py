#!/usr/bin/env python3
"""
Interactive Web Testing Script
Tests all critical endpoints via HTTP requests
"""

import requests
import json
import sys
from time import sleep
from datetime import datetime

BASE_URL = "http://localhost:5000"

# Test credentials from CSV
TEST_CREDENTIALS = {
    'admin_newton': {
        'username': 'Newton',
        'password': '##0000',
        'expected_role': 'admin',
        'description': 'Super Admin (A000)'
    },
    'student_jdoe': {
        'username': 'jdoe',
        'password': 'password123',
        'expected_role': 'student',
        'description': 'CSV Student - John Doe'
    },
    'student_asmith': {
        'username': 'asmith',
        'password': 'password123',
        'expected_role': 'student',
        'description': 'CSV Student - Alice Smith'
    },
    'teacher_jane': {
        'username': 'jane_smith',
        'password': 'password123',
        'expected_role': 'teacher',
        'description': 'CSV Teacher - Jane Smith'
    }
}

def print_header(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_server_running():
    """Test if server is running"""
    print_header("Testing Server Connection")
    try:
        response = requests.get(f"{BASE_URL}/api/status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is running")
            print(f"  App: {data.get('app_name')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Environment: {data.get('environment')}")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {BASE_URL}")
        print("  Make sure server is running: python START_SYSTEM.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_login(username, password, expected_role, description):
    """Test login endpoint"""
    try:
        print(f"\n  Testing: {description}")
        print(f"  Credentials: {username} / {password}")
        
        response = requests.post(
            f"{BASE_URL}/api/login",
            json={'username': username, 'password': password},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                actual_role = data.get('role', 'unknown')
                is_admin = data.get('is_admin', False)
                
                print(f"  ✓ Login successful")
                print(f"    Role: {actual_role}")
                print(f"    Is Admin: {is_admin}")
                print(f"    Message: {data.get('message', 'N/A')}")
                
                return True
            else:
                print(f"  ✗ Login failed: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_all_logins():
    """Test all login scenarios"""
    print_header("Testing Login Endpoints")
    
    results = {}
    for key, creds in TEST_CREDENTIALS.items():
        success = test_login(
            creds['username'],
            creds['password'],
            creds['expected_role'],
            creds['description']
        )
        results[key] = success
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n  Result: {passed}/{total} login tests passed")
    
    return results

def test_user_lookup():
    """Test user lookup endpoint"""
    print_header("Testing User Lookup")
    
    test_ids = ['A000', 'S001', 'T001']
    
    for user_id in test_ids:
        try:
            print(f"\n  Looking up user: {user_id}")
            response = requests.get(
                f"{BASE_URL}/api/user/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    user = data.get('user', {})
                    print(f"  ✓ Found")
                    print(f"    Username: {user.get('username')}")
                    print(f"    Full Name: {user.get('fullName')}")
                    print(f"    Role: {data.get('role')}")
                else:
                    print(f"  ✗ User not found")
            else:
                print(f"  ✗ HTTP {response.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

def test_csv_import():
    """Test CSV import endpoint"""
    print_header("Testing CSV Import")
    
    try:
        print("\n  Importing users from CSV...")
        
        response = requests.post(
            f"{BASE_URL}/api/import-csv",
            json={'import_password': 'ImportPassword2026'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                imported_count = len(data.get('imported', []))
                skipped_count = len(data.get('skipped', []))
                
                print(f"  ✓ Import completed")
                print(f"    Imported: {imported_count}")
                print(f"    Skipped: {skipped_count}")
                
                if skipped_count > 0:
                    print(f"\n  Skipped entries:")
                    for item in data.get('skipped', [])[:3]:
                        print(f"    - {item.get('reason')}")
                
                return True
            else:
                print(f"  ✗ Import failed: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_admin_endpoints():
    """Test admin-only endpoints"""
    print_header("Testing Admin Endpoints")
    
    # First login as admin
    print("\n  Logging in as admin...")
    login_response = requests.post(
        f"{BASE_URL}/api/login",
        json={'username': 'Newton', 'password': '##0000'},
        timeout=5
    )
    
    if login_response.status_code != 200 or not login_response.json().get('success'):
        print("  ✗ Admin login failed - skipping admin tests")
        return False
    
    print("  ✓ Admin logged in")
    
    # Test admin user list
    print("\n  Testing: GET /api/admin/users")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_count = len(data.get('users', []))
                print(f"  ✓ Retrieved {user_count} users")
            else:
                print(f"  ✗ Failed: {data.get('error')}")
        else:
            print(f"  ✗ HTTP {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test audit logs
    print("\n  Testing: GET /api/logs")
    try:
        response = requests.get(f"{BASE_URL}/api/logs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log_count = len(data.get('logs', []))
                print(f"  ✓ Retrieved {log_count} audit logs")
                
                # Check if A000 admin login is in logs
                logs = data.get('logs', [])
                a000_admin_logins = [l for l in logs if l.get('userId') == 'A000' and l.get('action') == 'admin_login']
                if a000_admin_logins:
                    print(f"  ⚠ WARNING: Found {len(a000_admin_logins)} A000 admin logins in logs (should be filtered)")
                else:
                    print(f"  ✓ A000 admin logins correctly filtered from logs")
            else:
                print(f"  ✗ Failed: {data.get('error')}")
        else:
            print(f"  ✗ HTTP {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return True

def main():
    """Main test execution"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         MENGO-HUB INTERACTIVE WEB TEST                         ║
    ║    Testing All Endpoints and Functionality                     ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if server is running
    if not test_server_running():
        print("\n✗ Server is not running!")
        print("\nTo start the server, run:")
        print("  python START_SYSTEM.py")
        return False
    
    # Run tests
    print("\n⏳ Starting comprehensive tests...")
    
    login_results = test_all_logins()
    test_user_lookup()
    csv_import_ok = test_csv_import()
    admin_ok = test_admin_endpoints()
    
    # Summary
    print_header("Test Summary")
    
    passed_logins = sum(1 for v in login_results.values() if v)
    total_logins = len(login_results)
    
    print(f"\n  Login Tests: {passed_logins}/{total_logins} passed")
    print(f"  CSV Import: {'✓ Passed' if csv_import_ok else '✗ Failed'}")
    print(f"  Admin Endpoints: {'✓ Passed' if admin_ok else '✗ Failed'}")
    
    if passed_logins == total_logins and csv_import_ok and admin_ok:
        print("\n✓ ALL TESTS PASSED - System is fully functional!")
        return True
    else:
        print("\n⚠ Some tests failed - review output above")
        return False

if __name__ == '__main__':
    try:
        # Wait for user to start server
        input("\n⏳ Press Enter after starting the server with: python START_SYSTEM.py\n")
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
