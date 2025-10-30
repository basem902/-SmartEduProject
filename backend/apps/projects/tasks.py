"""
Celery Tasks for AI Project Validation
"""
from celery import shared_task
from django.utils import timezone
import time
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_submission_with_ai(self, submission_id):
    """
    معالجة المشروع بالذكاء الاصطناعي
    
    Args:
        submission_id: معرف التسليم
    
    Returns:
        dict: نتائج المعالجة
    """
    from .models import Submission
    
    try:
        submission = Submission.objects.get(id=submission_id)
        start_time = time.time()
        
        logger.info(f"🔄 بدء معالجة Submission #{submission_id}")
        
        # تحديث الحالة
        submission.validation_status = 'processing'
        submission.save()
        
        # التحليل بالـ AI
        from .ai_validator import AIValidator
        validator = AIValidator()
        results = validator.validate_submission(submission)
        
        # حساب وقت المعالجة
        processing_time = time.time() - start_time
        
        # حفظ النتائج
        submission.validation_results = results
        submission.ai_score = results.get('overall_score', 0)
        submission.validation_status = results.get('status', 'rejected')
        submission.rejection_reasons = results.get('rejection_reasons', [])
        submission.processing_time = processing_time
        submission.processed_at = timezone.now()
        submission.ai_checked = True
        submission.save()
        
        logger.info(f"✅ انتهت معالجة Submission #{submission_id} - الحالة: {submission.validation_status}")
        
        # إرسال الإشعارات
        send_submission_notification.delay(submission_id)
        
        return {
            'submission_id': submission_id,
            'status': submission.validation_status,
            'score': float(submission.ai_score) if submission.ai_score else 0,
            'processing_time': processing_time
        }
        
    except Submission.DoesNotExist:
        logger.error(f"❌ Submission #{submission_id} غير موجود")
        return {'error': 'Submission not found'}
    
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة Submission #{submission_id}: {str(e)}")
        
        # إعادة المحاولة
        try:
            submission = Submission.objects.get(id=submission_id)
            submission.validation_status = 'pending'
            submission.save()
        except:
            pass
        
        # إعادة المحاولة بعد دقيقة
        raise self.retry(exc=e, countdown=60)


@shared_task
def send_submission_notification(submission_id):
    """
    إرسال إشعار Telegram حسب نتيجة التسليم
    
    Args:
        submission_id: معرف التسليم
    """
    from .models import Submission
    from .notifications import (
        send_accepted_notification,
        send_rejected_notification,
        send_review_notification
    )
    
    try:
        submission = Submission.objects.get(id=submission_id)
        
        if submission.validation_status == 'approved':
            send_accepted_notification(submission)
        elif submission.validation_status == 'rejected':
            send_rejected_notification(submission)
        elif submission.validation_status == 'needs_review':
            send_review_notification(submission)
        
        logger.info(f"📨 تم إرسال إشعار Submission #{submission_id}")
        
    except Submission.DoesNotExist:
        logger.error(f"❌ Submission #{submission_id} غير موجود")
    except Exception as e:
        logger.error(f"❌ خطأ في إرسال إشعار #{submission_id}: {str(e)}")


@shared_task
def check_submission_status(submission_id):
    """
    التحقق من حالة التسليم
    للاستخدام من Frontend
    
    Args:
        submission_id: معرف التسليم
    
    Returns:
        dict: حالة التسليم الحالية
    """
    from .models import Submission
    
    try:
        submission = Submission.objects.get(id=submission_id)
        
        return {
            'submission_id': submission_id,
            'status': submission.validation_status,
            'ai_score': float(submission.ai_score) if submission.ai_score else None,
            'rejection_reasons': submission.rejection_reasons,
            'processing_time': submission.processing_time,
            'processed_at': submission.processed_at.isoformat() if submission.processed_at else None
        }
        
    except Submission.DoesNotExist:
        return {'error': 'Submission not found'}
