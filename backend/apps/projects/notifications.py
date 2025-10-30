"""
Telegram Notifications for AI Submissions
"""
import os
import requests
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_telegram_message(bot_token, chat_id, message, parse_mode='Markdown'):
    """
    إرسال رسالة Telegram
    """
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"خطأ في إرسال رسالة Telegram: {str(e)}")
        return None


def send_accepted_notification(submission):
    """
    إشعار قبول المشروع
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return
    
    student_name = submission.submitted_student_name or submission.student.student_name
    project = submission.project
    
    # رسالة خاصة للطالب
    if hasattr(submission, 'student') and submission.student and hasattr(submission.student, 'telegram_chat_id'):
        private_message = f"""
✅ *تم قبول المشروع!*

عزيزي/عزيزتي: *{student_name}*
المشروع: *{project.title}*

📊 *النتائج:*
• التقييم: {submission.ai_score:.1f}/100
• المحاولة: {submission.attempt_number} من {project.max_attempts}
• وقت المعالجة: {submission.processing_time:.1f} ثانية

🎉 *تهانينا!*
مشروعك تم قبوله وسيتم مراجعته من قبل المعلم.

📅 تم التسليم: {submission.submitted_at.strftime('%Y-%m-%d %H:%M')}
"""
        send_telegram_message(bot_token, submission.student.telegram_chat_id, private_message)
    
    # رسالة في القروب
    sections = project.sections.all()
    for section in sections:
        if section.telegram_group_id:
            group_message = f"""
🎉 *تسليم جديد - مقبول*

الطالب: *{student_name}*
المشروع: *{project.title}*
التقييم: {submission.ai_score:.1f}/100

✅ تم القبول التلقائي
"""
            send_telegram_message(bot_token, section.telegram_group_id, group_message)


def send_rejected_notification(submission):
    """
    إشعار رفض المشروع
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return
    
    student_name = submission.submitted_student_name or submission.student.student_name
    project = submission.project
    
    # رسالة خاصة للطالب
    if hasattr(submission, 'student') and submission.student and hasattr(submission.student, 'telegram_chat_id'):
        reasons = "\n".join(f"  • {r}" for r in submission.rejection_reasons)
        
        remaining_attempts = project.max_attempts - submission.attempt_number
        time_left = project.deadline - timezone.now()
        days_left = time_left.days
        hours_left = time_left.seconds // 3600
        
        private_message = f"""
❌ *تم رفض المشروع*

عزيزي/عزيزتي: *{student_name}*
المشروع: *{project.title}*

❌ *أسباب الرفض:*
{reasons}

📊 *المحاولات:*
• رقم المحاولة: {submission.attempt_number} من {project.max_attempts}
• المحاولات المتبقية: {remaining_attempts}

⏰ *الوقت المتبقي:*
• باقي {days_left} يوم و {hours_left} ساعة
• آخر موعد: {project.deadline.strftime('%Y-%m-%d %H:%M')}

💡 *نصائح للتحسين:*
{get_improvement_suggestions(submission)}

📌 يمكنك المحاولة مرة أخرى من نفس الرابط
"""
        send_telegram_message(bot_token, submission.student.telegram_chat_id, private_message)


def send_review_notification(submission):
    """
    إشعار للمعلم - يحتاج مراجعة يدوية
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        return
    
    student_name = submission.submitted_student_name or submission.student.student_name
    project = submission.project
    
    # رسالة للمعلم
    if project.teacher.telegram_chat_id:
        teacher_message = f"""
⚠️ *مشروع يحتاج مراجعة يدوية*

الطالب: *{student_name}*
المشروع: *{project.title}*

🔍 *السبب:*
تشابه عالي مع مشاريع أخرى ({submission.validation_results.get('plagiarism', {}).get('max_similarity', 0):.1f}%)

📋 *التفاصيل:*
• التقييم: {submission.ai_score:.1f}/100
• المحاولة: {submission.attempt_number}

الرجاء المراجعة من لوحة التحكم
"""
        send_telegram_message(bot_token, project.teacher.telegram_chat_id, teacher_message)
    
    # رسالة للطالب
    if hasattr(submission, 'student') and submission.student and hasattr(submission.student, 'telegram_chat_id'):
        student_message = f"""
⏳ *المشروع قيد المراجعة*

عزيزي/عزيزتي: *{student_name}*
المشروع: *{project.title}*

مشروعك يحتاج إلى مراجعة يدوية من المعلم.
سيتم إشعارك بالنتيجة قريباً.

📅 تاريخ التسليم: {submission.submitted_at.strftime('%Y-%m-%d %H:%M')}
"""
        send_telegram_message(bot_token, submission.student.telegram_chat_id, student_message)


def get_improvement_suggestions(submission):
    """
    اقتراحات التحسين بناءً على أسباب الرفض
    """
    suggestions = []
    
    for reason in submission.rejection_reasons:
        if 'مدة' in reason or 'duration' in reason.lower():
            suggestions.append("• تأكد من أن مدة الفيديو ضمن المدى المطلوب")
        elif 'اسم' in reason or 'name' in reason.lower():
            suggestions.append("• اعرض اسمك بوضوح في آخر 5 ثواني من الفيديو")
        elif 'صف' in reason or 'grade' in reason.lower():
            suggestions.append("• أضف الصف والشعبة في آخر 5 ثواني")
        elif 'محتوى' in reason or 'content' in reason.lower():
            suggestions.append("• تأكد من أن المحتوى يطابق متطلبات المشروع")
        elif 'تشابه' in reason or 'similar' in reason.lower():
            suggestions.append("• قدم عمل أصلي من إبداعك الخاص")
    
    if not suggestions:
        suggestions.append("• راجع متطلبات المشروع بعناية")
        suggestions.append("• تأكد من جودة الملف")
    
    return "\n".join(suggestions)
