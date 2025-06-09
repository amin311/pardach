#!/usr/bin/env python
"""
🚀 اسکریپت جامع تست خودکار
این اسکریپت تمام تست‌های Backend و Frontend را به صورت خودکار اجرا می‌کند
"""
import subprocess
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# رنگ‌ها برای خروجی ترمینال
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """چاپ header با فرمت زیبا"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_step(step_num, total_steps, description):
    """چاپ مرحله فعلی"""
    print(f"{Colors.BOLD}{Colors.OKBLUE}[{step_num}/{total_steps}] {description}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def run_command(command, cwd=None, description="", timeout=300):
    """اجرای دستور با مدیریت خطا"""
    if description:
        print(f"   🔄 {description}...")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            if description:
                print_success(f"{description} موفق")
            return True, result.stdout
        else:
            if description:
                print_error(f"{description} ناموفق")
            print(f"خطا: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print_error(f"Timeout: {description}")
        return False, "Timeout"
    except Exception as e:
        print_error(f"خطا در اجرای {description}: {str(e)}")
        return False, str(e)

def check_prerequisites():
    """بررسی پیش‌نیازها"""
    print_step(1, 8, "بررسی پیش‌نیازها")
    
    # بررسی Python
    success, _ = run_command("python --version", description="بررسی Python")
    if not success:
        print_error("Python یافت نشد")
        return False
    
    # بررسی Node.js
    success, _ = run_command("node --version", description="بررسی Node.js")
    if not success:
        print_error("Node.js یافت نشد")
        return False
    
    # بررسی وجود پوشه‌ها
    required_dirs = ['backend', 'frontend']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print_error(f"پوشه {dir_name} یافت نشد")
            return False
    
    print_success("تمام پیش‌نیازها موجودند")
    return True

def setup_backend():
    """راه‌اندازی محیط Backend"""
    print_step(2, 8, "راه‌اندازی Backend")
    
    # فعال‌سازی virtual environment
    venv_path = "venv/Scripts/activate" if os.name == 'nt' else "venv/bin/activate"
    if os.path.exists(venv_path):
        print_success("Virtual environment یافت شد")
    else:
        print_warning("Virtual environment یافت نشد، ادامه بدون آن...")
    
    # بررسی Django
    success, _ = run_command("python backend/manage.py --version", description="بررسی Django")
    if not success:
        print_error("Django به درستی نصب نشده")
        return False
    
    return True

def setup_frontend():
    """راه‌اندازی محیط Frontend"""
    print_step(3, 8, "راه‌اندازی Frontend")
    
    # بررسی package.json
    if not os.path.exists("frontend/package.json"):
        print_error("package.json یافت نشد")
        return False
    
    # بررسی node_modules
    if not os.path.exists("frontend/node_modules"):
        print_warning("node_modules یافت نشد، نصب dependencies...")
        success, _ = run_command("npm install", cwd="frontend", description="نصب dependencies", timeout=600)
        if not success:
            print_error("نصب dependencies ناموفق")
            return False
    
    return True

def run_backend_tests():
    """اجرای تست‌های Backend"""
    print_step(4, 8, "اجرای تست‌های Backend")
    
    backend_results = {
        "django_tests": False,
        "security_check": False,
        "code_quality": False,
        "system_check": False
    }
    
    # Django system check
    success, _ = run_command(
        "python manage.py check --deploy",
        cwd="backend",
        description="بررسی سیستم Django"
    )
    backend_results["system_check"] = success
    
    # اجرای تست‌های Django
    success, _ = run_command(
        "python manage.py test --verbosity=2",
        cwd="backend",
        description="تست‌های Django",
        timeout=600
    )
    backend_results["django_tests"] = success
    
    # بررسی امنیتی (اختیاری)
    success, _ = run_command(
        "bandit -r apps/ -f json",
        cwd="backend",
        description="آنالیز امنیتی"
    )
    backend_results["security_check"] = success
    
    # بررسی کیفیت کد
    success, _ = run_command(
        "flake8 apps/ --count --select=E9,F63,F7,F82 --show-source --statistics",
        cwd="backend",
        description="بررسی کیفیت کد"
    )
    backend_results["code_quality"] = success
    
    return backend_results

def run_frontend_tests():
    """اجرای تست‌های Frontend"""
    print_step(5, 8, "اجرای تست‌های Frontend")
    
    frontend_results = {
        "lint": False,
        "unit_tests": False,
        "audit": False,
        "build": False
    }
    
    # Lint check
    success, _ = run_command(
        "npm run lint",
        cwd="frontend",
        description="بررسی ESLint"
    )
    frontend_results["lint"] = success
    
    # Unit tests
    success, _ = run_command(
        "npm run test:unit",
        cwd="frontend",
        description="تست‌های واحد",
        timeout=300
    )
    frontend_results["unit_tests"] = success
    
    # Security audit
    success, _ = run_command(
        "npm audit --audit-level moderate",
        cwd="frontend",
        description="بررسی امنیتی NPM"
    )
    frontend_results["audit"] = success
    
    # Build test
    success, _ = run_command(
        "npm run build",
        cwd="frontend",
        description="تست Build",
        timeout=600
    )
    frontend_results["build"] = success
    
    return frontend_results

def run_e2e_tests():
    """اجرای تست‌های End-to-End"""
    print_step(6, 8, "اجرای تست‌های E2E")
    
    # بررسی وجود Cypress
    if not os.path.exists("frontend/cypress"):
        print_warning("Cypress یافت نشد، E2E tests رد شد")
        return False
    
    # اجرای smoke tests
    success, _ = run_command(
        "npm run test:smoke",
        cwd="frontend",
        description="تست‌های Smoke",
        timeout=600
    )
    
    if success:
        # اجرای تمام E2E tests
        success, _ = run_command(
            "npm run cypress:run:headless",
            cwd="frontend",
            description="تست‌های E2E کامل",
            timeout=900
        )
    
    return success

def run_integration_tests():
    """اجرای تست‌های یکپارچگی"""
    print_step(7, 8, "تست‌های یکپارچگی")
    
    # تست API endpoints
    success, _ = run_command(
        "python test_login_api.py",
        description="تست API Login"
    )
    
    if success:
        success, _ = run_command(
            "python backend/test_apis.py",
            description="تست تمام API endpoints"
        )
    
    return success

def generate_report(backend_results, frontend_results, e2e_success, integration_success):
    """تولید گزارش نهایی"""
    print_step(8, 8, "تولید گزارش نهایی")
    
    total_tests = 0
    passed_tests = 0
    
    # Backend results
    for test, result in backend_results.items():
        total_tests += 1
        if result:
            passed_tests += 1
    
    # Frontend results
    for test, result in frontend_results.items():
        total_tests += 1
        if result:
            passed_tests += 1
    
    # E2E and Integration
    total_tests += 2
    if e2e_success:
        passed_tests += 1
    if integration_success:
        passed_tests += 1
    
    # محاسبه درصد موفقیت
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    # گزارش
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": success_rate,
        "backend": backend_results,
        "frontend": frontend_results,
        "e2e": e2e_success,
        "integration": integration_success
    }
    
    # ذخیره گزارش
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def main():
    """تابع اصلی"""
    start_time = time.time()
    
    print_header("🚀 سیستم تست خودکار جامع")
    print(f"شروع تست در: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # بررسی پیش‌نیازها
    if not check_prerequisites():
        print_error("پیش‌نیازها برآورده نشده")
        sys.exit(1)
    
    # راه‌اندازی Backend
    if not setup_backend():
        print_error("راه‌اندازی Backend ناموفق")
        sys.exit(1)
    
    # راه‌اندازی Frontend
    if not setup_frontend():
        print_error("راه‌اندازی Frontend ناموفق")
        sys.exit(1)
    
    # اجرای تست‌ها
    backend_results = run_backend_tests()
    frontend_results = run_frontend_tests()
    e2e_success = run_e2e_tests()
    integration_success = run_integration_tests()
    
    # تولید گزارش
    report = generate_report(backend_results, frontend_results, e2e_success, integration_success)
    
    # نمایش نتایج
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("📊 نتایج نهایی")
    print(f"⏱️  زمان کل: {duration:.2f} ثانیه")
    print(f"📈 نرخ موفقیت: {report['success_rate']:.1f}%")
    print(f"✅ تست‌های موفق: {report['passed_tests']}")
    print(f"📝 کل تست‌ها: {report['total_tests']}")
    
    print("\n🔍 جزئیات:")
    print("Backend:")
    for test, result in backend_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    print("Frontend:")
    for test, result in frontend_results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {test}")
    
    print(f"E2E Tests: {'✅' if e2e_success else '❌'}")
    print(f"Integration Tests: {'✅' if integration_success else '❌'}")
    
    print(f"\n📄 گزارش کامل در فایل test_report.json ذخیره شد")
    
    if report['success_rate'] >= 80:
        print_success("🎉 تست‌ها با موفقیت کامل شدند!")
        sys.exit(0)
    else:
        print_warning("⚠️ برخی تست‌ها نیاز به بررسی دارند")
        sys.exit(1)

if __name__ == "__main__":
    main() 