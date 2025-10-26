#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated Testing Script for OTP System
تشغيل اختبارات شاملة للنظام
"""
import requests
import time
import json
from colorama import init, Fore, Style
import sys
import os

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

# Initialize colorama
init(autoreset=True)

# Configuration
API_BASE = 'http://localhost:8000/api'
TEST_DATA = {
    'project_id': 1,
    'student_id': 1,
    'telegram_user_id': '123456789'
}

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.results = []
        
    def print_header(self, text):
        """طباعة عنوان"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{text.center(60)}")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def print_test(self, name):
        """طباعة اسم الاختبار"""
        print(f"{Fore.YELLOW}[TEST] Testing: {name}...", end=' ')
        
    def print_success(self, message=''):
        """طباعة نجاح"""
        self.passed += 1
        self.total += 1
        print(f"{Fore.GREEN}[PASS] {message}")
        
    def print_fail(self, error=''):
        """طباعة فشل"""
        self.failed += 1
        self.total += 1
        print(f"{Fore.RED}[FAIL] {error}")
        
    def print_info(self, message):
        """طباعة معلومة"""
        print(f"{Fore.BLUE}[INFO] {message}")
        
    def print_warning(self, message):
        """طباعة تحذير"""
        print(f"{Fore.YELLOW}[WARN] {message}")
    
    def test_backend_running(self):
        """اختبار: Backend يعمل"""
        self.print_test("Backend Running")
        try:
            response = requests.get(f'{API_BASE.replace("/api", "")}/admin/', timeout=5)
            if response.status_code in [200, 302, 404]:
                self.print_success()
                return True
            else:
                self.print_fail(f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"Error: {str(e)}")
            return False
    
    def test_generate_otp(self):
        """اختبار: توليد OTP"""
        self.print_test("Generate OTP")
        try:
            response = requests.post(
                f'{API_BASE}/otp/init/',
                json=TEST_DATA,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('otp_code'):
                    self.print_success(f"OTP: {data['otp_code']}")
                    return data['otp_code']
                else:
                    self.print_fail("No OTP code in response")
                    return None
            else:
                self.print_fail(f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_fail(f"Error: {str(e)}")
            return None
    
    def test_validate_otp(self, otp_code):
        """اختبار: التحقق من OTP"""
        self.print_test("Validate OTP")
        try:
            response = requests.post(
                f'{API_BASE}/otp/verify/',
                json={
                    'otp_code': otp_code,
                    'project_id': TEST_DATA['project_id']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid') and data.get('token'):
                    self.print_success("Token received")
                    return data['token']
                else:
                    self.print_fail("Invalid OTP")
                    return None
            else:
                self.print_fail(f"Status: {response.status_code}")
                return None
        except Exception as e:
            self.print_fail(f"Error: {str(e)}")
            return None
    
    def test_invalid_otp(self):
        """اختبار: OTP خاطئ"""
        self.print_test("Invalid OTP Rejection")
        try:
            response = requests.post(
                f'{API_BASE}/otp/verify/',
                json={
                    'otp_code': '999999',
                    'project_id': TEST_DATA['project_id']
                },
                timeout=10
            )
            
            data = response.json()
            if not data.get('valid', True):
                self.print_success("Correctly rejected")
                return True
            else:
                self.print_fail("Accepted invalid OTP!")
                return False
        except Exception as e:
            self.print_fail(f"Error: {str(e)}")
            return False
    
    def test_duplicate_otp_usage(self, otp_code):
        """اختبار: استخدام OTP مرتين"""
        self.print_test("Duplicate OTP Usage")
        try:
            # First use
            requests.post(
                f'{API_BASE}/otp/verify/',
                json={
                    'otp_code': otp_code,
                    'project_id': TEST_DATA['project_id']
                },
                timeout=10
            )
            
            # Second use (should fail)
            time.sleep(1)
            response = requests.post(
                f'{API_BASE}/otp/verify/',
                json={
                    'otp_code': otp_code,
                    'project_id': TEST_DATA['project_id']
                },
                timeout=10
            )
            
            data = response.json()
            if not data.get('valid', True):
                self.print_success("Correctly rejected duplicate")
                return True
            else:
                self.print_fail("Accepted duplicate OTP!")
                return False
        except Exception as e:
            self.print_fail(f"Error: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """اختبار: جميع API endpoints"""
        endpoints = [
            ('/otp/init/', 'POST'),
            ('/otp/verify/', 'POST'),
            ('/projects/submit/', 'POST'),
        ]
        
        for endpoint, method in endpoints:
            self.print_test(f"{method} {endpoint}")
            try:
                url = f'{API_BASE}{endpoint}'
                # Just check if endpoint exists (will return 400/405 but not 404)
                if method == 'POST':
                    response = requests.post(url, json={}, timeout=5)
                else:
                    response = requests.get(url, timeout=5)
                
                if response.status_code != 404:
                    self.print_success(f"Endpoint exists")
                else:
                    self.print_fail("Endpoint not found")
            except Exception as e:
                self.print_fail(f"Error: {str(e)}")
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        self.print_header("Starting Automated Tests")
        
        # Test 1: Backend Running
        if not self.test_backend_running():
            self.print_warning("Backend not running. Some tests will fail.")
            self.print_info("Start backend: cd backend && python manage.py runserver")
            return
        
        # Test 2: API Endpoints
        self.print_header("Testing API Endpoints")
        self.test_api_endpoints()
        
        # Test 3: Generate OTP
        self.print_header("Testing OTP Generation")
        otp_code = self.test_generate_otp()
        
        if otp_code:
            # Test 4: Validate OTP
            self.print_header("Testing OTP Validation")
            token = self.test_validate_otp(otp_code)
            
            # Test 5: Invalid OTP
            self.test_invalid_otp()
        else:
            self.print_warning("Skipping validation tests - no OTP generated")
        
        # Test 6: Duplicate OTP
        self.print_header("Testing Security")
        otp_code2 = self.test_generate_otp()
        if otp_code2:
            self.test_duplicate_otp_usage(otp_code2)
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """طباعة ملخص النتائج"""
        self.print_header("Test Results Summary")
        
        print(f"{Fore.CYAN}Total Tests: {self.total}")
        print(f"{Fore.GREEN}Passed: {self.passed}")
        print(f"{Fore.RED}Failed: {self.failed}")
        
        if self.failed == 0:
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}{'*** ALL TESTS PASSED! ***'.center(60)}")
            print(f"{Fore.GREEN}{'='*60}\n")
        else:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}{'*** SOME TESTS FAILED ***'.center(60)}")
            print(f"{Fore.RED}{'='*60}\n")
            
        # Success Rate
        if self.total > 0:
            rate = (self.passed / self.total) * 100
            print(f"{Fore.CYAN}Success Rate: {rate:.1f}%\n")

def main():
    """Main function"""
    print(f"{Fore.CYAN}")
    print("=" * 60)
    print(" OTP System Automated Testing ".center(60))
    print("=" * 60)
    print(Style.RESET_ALL)
    
    runner = TestRunner()
    
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user")
        runner.print_summary()
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {str(e)}")
        runner.print_summary()

if __name__ == '__main__':
    main()
