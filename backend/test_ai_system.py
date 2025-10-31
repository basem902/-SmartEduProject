"""
🧪 Test AI Submission System - الاختبار الشامل
اختبار نظام AI لاستلام المشاريع - جميع أنواع الملفات
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.projects.ai_validator import AIValidator
from apps.projects.models import Project, Submission
from apps.sections.models import StudentRegistration

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

def test_file_validation(file_type='all'):
    """
    اختبار التحقق من الملفات
    
    Args:
        file_type: نوع الملف للاختبار (video/pdf/image/document/audio/all)
    """
    print("\n" + "=" * 60)
    print(f"🔍 اختبار التحقق من الملفات: {file_type}")
    print("=" * 60)
    
    try:
        validator = AIValidator()
        
        # فلترة التسليمات حسب النوع
        if file_type == 'all':
            submissions = Submission.objects.all()[:5]
        else:
            submissions = Submission.objects.filter(file_type=file_type)[:3]
        
        if not submissions.exists():
            print(f"\n⚠️ لا توجد تسليمات من نوع '{file_type}' للاختبار")
            print("💡 نصيحة: قم برفع ملفات تجريبية من خلال الموقع أولاً")
            return
        
        print(f"\n📊 عدد التسليمات: {submissions.count()}")
        
        for submission in submissions:
            print(f"\n{'='*50}")
            print(f"📝 اختبار التسليم #{submission.id}")
            print(f"   • نوع الملف: {submission.file_type}")
            print(f"   • الطالب: {submission.submitted_student_name}")
            print(f"   • المشروع: {submission.project.title}")
            print(f"   • الحالة: {submission.status}")
            
            # تنفيذ التحقق حسب نوع الملف
            print(f"\n⚙️ بدء التحقق...")
            start_time = datetime.now()
            
            try:
                if submission.file_type == 'video':
                    result = validator.validate_video(submission)
                elif submission.file_type == 'pdf':
                    result = validator.validate_pdf(submission)
                elif submission.file_type == 'image':
                    result = validator.validate_image(submission)
                elif submission.file_type in ['document', 'word', 'excel', 'powerpoint']:
                    result = validator.validate_document(submission)
                elif submission.file_type == 'audio':
                    result = validator.validate_audio(submission)
                else:
                    print(f"❌ نوع ملف غير مدعوم: {submission.file_type}")
                    continue
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # عرض النتائج
                print(f"\n{'🎉' if result['status'] == 'approved' else '❌'} النتيجة:")
                print(f"   • الحالة: {result['status']}")
                print(f"   • الدرجة: {result['overall_score']:.1f}%")
                print(f"   • الوقت: {duration:.2f} ثانية")
                
                if result.get('checks'):
                    print(f"\n   📋 الفحوصات:")
                    for check_name, check_data in result['checks'].items():
                        status_emoji = "✅" if check_data.get('status') == 'pass' else "⚠️" if check_data.get('status') == 'warning' else "❌"
                        print(f"      {status_emoji} {check_name}: {check_data.get('message', 'N/A')}")
                
                if result.get('rejection_reasons'):
                    print(f"\n   ❌ أسباب الرفض:")
                    for reason in result['rejection_reasons']:
                        print(f"      • {reason}")
                
                if result.get('warnings'):
                    print(f"\n   ⚠️ تحذيرات:")
                    for warning in result['warnings']:
                        print(f"      • {warning}")
                
            except Exception as e:
                print(f"\n❌ خطأ في التحقق: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*50}")
        print("✅ اكتمل اختبار الملفات")
        
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

def check_libraries():
    """التحقق من المكتبات المطلوبة"""
    print("\n" + "=" * 60)
    print("📚 التحقق من المكتبات")
    print("=" * 60)
    
    libraries = {
        '🤖 AI & ML': [
            ('google.generativeai', 'Gemini AI'),
            ('easyocr', 'EasyOCR'),
        ],
        '🎬 Video': [
            ('cv2', 'OpenCV'),
            ('moviepy.editor', 'MoviePy'),
            ('videohash', 'VideoHash'),
        ],
        '📄 PDF': [
            ('pdfplumber', 'PDFPlumber'),
            ('PyPDF2', 'PyPDF2'),
        ],
        '🖼️ Image': [
            ('imagehash', 'ImageHash'),
            ('PIL', 'Pillow'),
        ],
        '📝 Document': [
            ('docx', 'python-docx'),
            ('openpyxl', 'openpyxl'),
            ('pptx', 'python-pptx'),
        ],
        '🎵 Audio': [
            ('pydub', 'pydub'),
            ('speech_recognition', 'SpeechRecognition'),
        ],
        '🔢 ML': [
            ('sklearn', 'scikit-learn'),
            ('numpy', 'numpy'),
        ]
    }
    
    all_ok = True
    
    for category, libs in libraries.items():
        print(f"\n{category}:")
        for module_name, display_name in libs:
            try:
                __import__(module_name)
                print(f"   ✅ {display_name}")
            except ImportError:
                print(f"   ❌ {display_name} (غير مثبت)")
                all_ok = False
    
    if all_ok:
        print(f"\n✅ جميع المكتبات مثبتة!")
    else:
        print(f"\n⚠️ بعض المكتبات غير مثبتة")
        print(f"💡 قم بتثبيتها: pip install -r requirements.txt")

def test_by_file_type():
    """قائمة تفاعلية لاختبار أنواع الملفات"""
    print("\n" + "=" * 60)
    print("🎯 اختر نوع الملف للاختبار")
    print("=" * 60)
    
    print("\n1️⃣  فيديو (Video)")
    print("2️⃣  PDF")
    print("3️⃣  صورة (Image)")
    print("4️⃣  مستندات (Word/Excel/PPT)")
    print("5️⃣  صوت (Audio)")
    print("6️⃣  جميع الأنواع (All)")
    print("0️⃣  تخطي")
    
    choice = input("\nاختر رقم: ").strip()
    
    type_map = {
        '1': 'video',
        '2': 'pdf',
        '3': 'image',
        '4': 'document',
        '5': 'audio',
        '6': 'all',
        '0': None
    }
    
    file_type = type_map.get(choice)
    
    if file_type:
        test_file_validation(file_type)
    else:
        print("⏭️ تم التخطي")

def create_test_data():
    """إنشاء بيانات تجريبية"""
    print("\n" + "=" * 60)
    print("🔧 إنشاء بيانات تجريبية")
    print("=" * 60)
    
    try:
        from django.utils import timezone
        from datetime import timedelta
        
        # إنشاء مشروع تجريبي
        project, created = Project.objects.get_or_create(
            title="مشروع اختبار AI",
            defaults={
                'description': 'مشروع لاختبار نظام الذكاء الاصطناعي',
                'file_type': 'video',
                'deadline': timezone.now() + timedelta(days=30),  # deadline بعد 30 يوم
                'ai_validation_enabled': True,
                'max_attempts': 3,
                'plagiarism_threshold': 70,
                'file_constraints': {
                    'duration': {'min': 15, 'max': 30},
                    'min_words': 100,
                    'max_words': 5000
                }
            }
        )
        
        if created:
            print(f"✅ تم إنشاء مشروع تجريبي: {project.title} (ID: {project.id})")
        else:
            print(f"ℹ️ المشروع التجريبي موجود مسبقاً (ID: {project.id})")
        
        # إنشاء طالب تجريبي
        student, created = StudentRegistration.objects.get_or_create(
            telegram_user_id=123456789,
            defaults={
                'full_name': 'طالب تجريبي',
                'telegram_username': 'test_student'
            }
        )
        
        if created:
            print(f"✅ تم إنشاء طالب تجريبي: {student.full_name}")
        else:
            print(f"ℹ️ الطالب التجريبي موجود مسبقاً")
        
        print(f"\n💡 يمكنك الآن رفع ملفات للمشروع ID: {project.id}")
        
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n" + "🎯" * 30)
    print("🧪 نظام اختبار الذكاء الاصطناعي الشامل")
    print("🎯" * 30)
    
    # اختبارات أساسية
    check_libraries()
    test_ai_validator()
    check_models()
    
    # إنشاء بيانات تجريبية إذا لزم الأمر
    print("\n" + "=" * 60)
    create_data = input("هل تريد إنشاء بيانات تجريبية؟ (y/n): ").lower()
    if create_data == 'y':
        create_test_data()
    
    # اختبار أنواع الملفات
    test_by_file_type()
    
    print("\n" + "=" * 60)
    print("🎉 انتهى الاختبار!")
    print("=" * 60)
