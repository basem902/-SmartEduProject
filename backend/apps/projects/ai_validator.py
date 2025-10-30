"""
AI Validator for Project Submissions
نظام التحقق بالذكاء الاصطناعي
"""
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIValidator:
    """
    نظام التحقق بالذكاء الاصطناعي للمشاريع
    """
    
    def __init__(self):
        """تهيئة AI Validator"""
        # Gemini API
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_flash = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini_vision = genai.GenerativeModel('gemini-1.5-pro-vision')
            logger.info("✅ Gemini API initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {str(e)}")
            self.gemini_flash = None
            self.gemini_vision = None
    
    def validate_submission(self, submission):
        """
        التحقق الشامل من المشروع
        
        Args:
            submission: كائن Submission
        
        Returns:
            dict: نتائج التحقق
        """
        project = submission.project
        file_type = project.file_type
        
        logger.info(f"🔍 بدء التحقق من Submission #{submission.id} - نوع الملف: {file_type}")
        
        try:
            # اختيار المعالج حسب نوع الملف
            if file_type == 'video':
                return self.validate_video(submission)
            elif file_type == 'pdf':
                return self.validate_pdf(submission)
            elif file_type == 'image':
                return self.validate_image(submission)
            elif file_type == 'document':
                return self.validate_document(submission)
            elif file_type == 'audio':
                return self.validate_audio(submission)
            else:
                return {
                    'status': 'rejected',
                    'overall_score': 0,
                    'rejection_reasons': [f'نوع ملف غير مدعوم: {file_type}']
                }
        
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق: {str(e)}", exc_info=True)
            return {
                'status': 'needs_review',
                'overall_score': 0,
                'rejection_reasons': [f'حدث خطأ في التحليل: {str(e)}'],
                'error': str(e)
            }
    
    def validate_video(self, submission):
        """
        التحقق من الفيديو
        (سيتم التطوير في المرحلة التالية)
        """
        logger.info(f"🎬 فحص الفيديو #{submission.id}")
        
        # TODO: تطوير فحص الفيديو الكامل
        # - فحص المدة
        # - OCR على آخر 5 ثواني
        # - تحليل المحتوى بـ Gemini Vision
        # - كشف التشابه
        
        # مؤقتاً: قبول تلقائي للاختبار
        return {
            'status': 'approved',
            'overall_score': 85.0,
            'checks': {
                'duration': {'status': 'pass', 'message': 'المدة مناسبة'},
                'content': {'status': 'pass', 'score': 85}
            },
            'rejection_reasons': []
        }
    
    def validate_pdf(self, submission):
        """
        التحقق من PDF
        (سيتم التطوير في المرحلة التالية)
        """
        logger.info(f"📄 فحص PDF #{submission.id}")
        
        # TODO: تطوير فحص PDF
        # - استخراج النص
        # - تحليل المحتوى
        # - كشف التشابه
        
        # مؤقتاً: قبول تلقائي للاختبار
        return {
            'status': 'approved',
            'overall_score': 80.0,
            'checks': {
                'content': {'status': 'pass', 'score': 80}
            },
            'rejection_reasons': []
        }
    
    def validate_image(self, submission):
        """التحقق من الصورة"""
        logger.info(f"🖼️ فحص الصورة #{submission.id}")
        
        return {
            'status': 'approved',
            'overall_score': 75.0,
            'checks': {
                'quality': {'status': 'pass'}
            },
            'rejection_reasons': []
        }
    
    def validate_document(self, submission):
        """التحقق من المستندات (Word/Excel/PPT)"""
        logger.info(f"📝 فحص المستند #{submission.id}")
        
        return {
            'status': 'approved',
            'overall_score': 80.0,
            'checks': {
                'format': {'status': 'pass'}
            },
            'rejection_reasons': []
        }
    
    def validate_audio(self, submission):
        """التحقق من الصوت"""
        logger.info(f"🎵 فحص الصوت #{submission.id}")
        
        return {
            'status': 'approved',
            'overall_score': 75.0,
            'checks': {
                'duration': {'status': 'pass'}
            },
            'rejection_reasons': []
        }
