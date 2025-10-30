"""
Test AI Submission System
اختبار نظام AI لاستلام المشاريع
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.projects.ai_validator import AIValidator
from apps.projects.models import Project, Submission

def test_ai_validator():
    """اختبار AI Validator"""
    print("=" * 60)
    print("🤖 اختبار AI Validator")
    print("=" * 60)
    
    try:
        validator = AIValidator()
        print("\n✅ تم إنشاء AIValidator بنجاح")
        
        # اختبار Gemini
        if validator.gemini_flash:
            print("✅ Gemini Flash متاح")
        else:
            print("⚠️ Gemini Flash غير متاح")
        
        if validator.gemini_vision:
            print("✅ Gemini Vision متاح")
        else:
            print("⚠️ Gemini Vision غير متاح")
        
        print("\n" + "=" * 60)
        print("✅ الاختبار نجح!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

def test_celery_task():
    """اختبار Celery Task"""
    print("\n" + "=" * 60)
    print("⚙️ اختبار Celery")
    print("=" * 60)
    
    try:
        from apps.projects.tasks import process_submission_with_ai
        print("✅ تم استيراد Celery Task بنجاح")
        
        # تحقق من Celery app
        from config.celery import app as celery_app
        print(f"✅ Celery App: {celery_app.main}")
        
        # تحقق من Redis connection
        result = celery_app.control.ping()
        if result:
            print(f"✅ Celery Workers: {result}")
        else:
            print("⚠️ لا يوجد Celery Workers نشطة (قم بتشغيل: celery -A config worker)")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

def check_models():
    """التحقق من Models"""
    print("\n" + "=" * 60)
    print("📊 التحقق من Models")
    print("=" * 60)
    
    try:
        # عد المشاريع
        projects_count = Project.objects.count()
        print(f"\n📁 عدد المشاريع: {projects_count}")
        
        # عد التسليمات
        submissions_count = Submission.objects.count()
        print(f"📤 عدد التسليمات: {submissions_count}")
        
        # عرض آخر مشروع
        if projects_count > 0:
            last_project = Project.objects.latest('created_at')
            print(f"\n📌 آخر مشروع:")
            print(f"   • ID: {last_project.id}")
            print(f"   • العنوان: {last_project.title}")
            print(f"   • نوع الملف: {last_project.file_type}")
            print(f"   • AI مفعّل: {last_project.ai_validation_enabled}")
            print(f"   • عدد المحاولات: {last_project.max_attempts}")
        
        print("\n✅ Models تعمل بشكل صحيح")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n🚀 بدء الاختبار الشامل\n")
    
    test_ai_validator()
    test_celery_task()
    check_models()
    
    print("\n" + "=" * 60)
    print("🎉 انتهى الاختبار!")
    print("=" * 60)
