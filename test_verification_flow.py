"""
سكريبت اختبار تدفق التحقق من الطلاب
"""

import os
import sys
import requests
import json

# الإعدادات
API_URL = "http://localhost:8000/api"
SECTION_ID = 1  # غيّر هذا حسب الشعبة المراد اختبارها

def test_verify_student():
    """
    اختبار API التحقق من الطالب
    """
    print("\n" + "=" * 60)
    print("🧪 اختبار التحقق من الطالب")
    print("=" * 60)
    
    # حالة 1: طالب موجود
    print("\n1️⃣ اختبار: طالب موجود")
    data = {
        "student_name": "ريماس باسم محمد الحجري",  # غيّر هذا للاسم الموجود
        "section_id": SECTION_ID
    }
    
    try:
        response = requests.post(
            f"{API_URL}/sections/verify-student-join/",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        print(f"📡 الحالة: {response.status_code}")
        print(f"📊 النتيجة:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get('success'):
            print("\n✅ النجاح: الطالب موجود!")
            print(f"   الاسم: {result['student']['name']}")
            print(f"   الصف: {result['student']['grade']}")
            print(f"   الشعبة: {result['student']['section']}")
            if result.get('telegram_group'):
                print(f"   رابط القروب: {result['telegram_group']['invite_link']}")
        else:
            print(f"\n❌ الفشل: {result.get('message')}")
            
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
    
    # حالة 2: طالب غير موجود
    print("\n2️⃣ اختبار: طالب غير موجود")
    data = {
        "student_name": "خالد سعيد عبدالله محمد",
        "section_id": SECTION_ID
    }
    
    try:
        response = requests.post(
            f"{API_URL}/sections/verify-student-join/",
            json=data
        )
        
        result = response.json()
        print(f"📡 الحالة: {response.status_code}")
        
        if not result.get('success'):
            print(f"✅ متوقع: الطالب غير موجود")
            print(f"   الرسالة: {result.get('message')}")
            if result.get('suggestions'):
                print(f"   الاقتراحات: {len(result['suggestions'])} أسماء")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
    
    # حالة 3: اسم مشابه
    print("\n3️⃣ اختبار: اسم مشابه")
    data = {
        "student_name": "ريماس باسم محمد الحجيري",  # خطأ طفيف في الاسم
        "section_id": SECTION_ID
    }
    
    try:
        response = requests.post(
            f"{API_URL}/sections/verify-student-join/",
            json=data
        )
        
        result = response.json()
        print(f"📡 الحالة: {response.status_code}")
        
        if not result.get('success') and result.get('suggestions'):
            print(f"✅ متوقع: وُجدت اقتراحات")
            for s in result['suggestions']:
                print(f"   • {s['name']} ({s['similarity']}% تشابه)")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")


def test_confirm_join():
    """
    اختبار API تأكيد الانضمام
    """
    print("\n" + "=" * 60)
    print("🧪 اختبار تأكيد انضمام الطالب")
    print("=" * 60)
    
    data = {
        "student_id": 6,  # غيّر هذا لـ ID الطالب الحقيقي
        "telegram_user_id": 123456789,
        "telegram_username": "test_student",
        "chat_id": -1001234567890
    }
    
    try:
        response = requests.post(
            f"{API_URL}/sections/confirm-student-joined/",
            json=data
        )
        
        result = response.json()
        print(f"📡 الحالة: {response.status_code}")
        print(f"📊 النتيجة:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get('success'):
            print("\n✅ النجاح: تم تحديث بيانات الطالب!")
        else:
            print(f"\n❌ الفشل: {result.get('message')}")
            
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")


def check_students_status():
    """
    عرض حالة الطلاب في Database
    """
    print("\n" + "=" * 60)
    print("📊 حالة الطلاب في Database")
    print("=" * 60)
    
    # يحتاج Django setup
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()
        
        from apps.sections.models import StudentRegistration
        
        students = StudentRegistration.objects.filter(section_id=SECTION_ID)
        
        print(f"\n📈 إجمالي الطلاب في الشعبة {SECTION_ID}: {students.count()}")
        print(f"   ✅ انضموا للتليجرام: {students.filter(joined_telegram=True).count()}")
        print(f"   ⏳ لم ينضموا بعد: {students.filter(joined_telegram=False).count()}")
        
        print(f"\n📋 قائمة الطلاب:")
        for student in students:
            status = "✅" if student.joined_telegram else "⏳"
            print(f"   {status} {student.full_name}")
            if student.joined_telegram:
                print(f"      └─ @{student.telegram_username or 'N/A'} (ID: {student.telegram_user_id})")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        print("💡 تأكد أن Backend مُعدّ بشكل صحيح")


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════╗
║          🧪 سكريبت اختبار نظام التحقق من الطلاب          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("📝 تأكد من:")
    print("   1. Backend يعمل: python manage.py runserver")
    print("   2. Database محدّث")
    print("   3. يوجد طلاب في الشعبة المختارة")
    print()
    
    input("اضغط Enter للبدء...")
    
    # تشغيل الاختبارات
    test_verify_student()
    test_confirm_join()
    check_students_status()
    
    print("\n" + "=" * 60)
    print("✅ انتهى الاختبار!")
    print("=" * 60)
    print()
