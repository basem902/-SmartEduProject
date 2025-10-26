"""
Tests for OTP System
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.projects.models import Project
from apps.sections.models import Grade, Section, SectionLink
from apps.accounts.models import Teacher
from .models import ProjectOTP, OTPLog
from .utils import OTPGenerator, SignatureHelper


class OTPGeneratorTest(TestCase):
    """اختبار مولد OTP"""
    
    def test_generate_code(self):
        """اختبار توليد كود"""
        code = OTPGenerator.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
    
    def test_is_code_valid(self):
        """اختبار صحة الكود"""
        self.assertTrue(OTPGenerator.is_code_valid('123456'))
        self.assertFalse(OTPGenerator.is_code_valid('12345'))
        self.assertFalse(OTPGenerator.is_code_valid('abc123'))
        self.assertFalse(OTPGenerator.is_code_valid(''))
    
    def test_generate_submit_token(self):
        """اختبار توليد رمز التسليم"""
        token = OTPGenerator.generate_submit_token()
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 20)


class SignatureHelperTest(TestCase):
    """اختبار التوقيع"""
    
    def test_sign_and_verify(self):
        """اختبار التوقيع والتحقق"""
        data = "test_data"
        signed = SignatureHelper.sign_data(data)
        verified = SignatureHelper.verify_signature(signed)
        self.assertEqual(verified, data)
    
    def test_verify_invalid_signature(self):
        """اختبار التحقق من توقيع خاطئ"""
        signed = "data|invalidsignature"
        verified = SignatureHelper.verify_signature(signed)
        self.assertIsNone(verified)


class ProjectOTPModelTest(TestCase):
    """اختبار نموذج ProjectOTP"""
    
    def setUp(self):
        """إعداد البيانات للاختبار"""
        # إنشاء معلم
        self.teacher = Teacher.objects.create(
            email='teacher@test.com',
            full_name='معلم تجريبي',
            phone='0500000000'
        )
        
        # إنشاء صف وشعبة
        self.grade = Grade.objects.create(
            teacher=self.teacher,
            level='intermediate',
            grade_number=1,
            display_name='الأول متوسط'
        )
        
        self.section = Section.objects.create(
            grade=self.grade,
            section_number=1,
            section_name='شعبة 1'
        )
        
        # إنشاء مشروع
        self.project = Project.objects.create(
            teacher=self.teacher,
            section=self.section,
            title='مشروع تجريبي',
            description='وصف',
            subject='علوم',
            grade='أول متوسط',
            deadline=timezone.now() + timedelta(days=7)
        )
    
    def test_create_otp(self):
        """اختبار إنشاء OTP"""
        otp = ProjectOTP.objects.create(
            project=self.project,
            student_name='محمد',
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=10),
            signed_payload='test'
        )
        
        self.assertEqual(otp.status, 'pending')
        self.assertEqual(otp.attempts, 0)
        self.assertFalse(otp.is_expired())
    
    def test_is_expired(self):
        """اختبار انتهاء الصلاحية"""
        # OTP منتهي
        expired_otp = ProjectOTP.objects.create(
            project=self.project,
            student_name='أحمد',
            code='654321',
            expires_at=timezone.now() - timedelta(minutes=1),
            signed_payload='test'
        )
        
        self.assertTrue(expired_otp.is_expired())
    
    def test_increment_attempts(self):
        """اختبار زيادة المحاولات"""
        otp = ProjectOTP.objects.create(
            project=self.project,
            student_name='علي',
            code='111111',
            expires_at=timezone.now() + timedelta(minutes=10),
            signed_payload='test',
            max_attempts=5
        )
        
        initial_attempts = otp.attempts
        otp.increment_attempts()
        
        self.assertEqual(otp.attempts, initial_attempts + 1)
    
    def test_mark_as_verified(self):
        """اختبار تحديد كتم التحقق"""
        otp = ProjectOTP.objects.create(
            project=self.project,
            student_name='فاطمة',
            code='222222',
            expires_at=timezone.now() + timedelta(minutes=10),
            signed_payload='test'
        )
        
        otp.mark_as_verified()
        
        self.assertEqual(otp.status, 'verified')
        self.assertIsNotNone(otp.submit_token)
        self.assertIsNotNone(otp.verified_at)


# يمكن إضافة المزيد من الاختبارات للـ APIs
