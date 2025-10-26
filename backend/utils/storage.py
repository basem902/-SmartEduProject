"""
نظام رفع وتخزين الملفات الآمن
"""
import os
import uuid
import logging
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ValidationError
from .av import av_scanner
from .validation import InputValidator

# محاولة استيراد python-magic (اختياري)
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class SecureFileUpload:
    """رفع الملفات بشكل آمن"""
    
    def __init__(self):
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self.max_size = settings.MAX_UPLOAD_SIZE
        
        # MIME types المسموحة
        self.allowed_mime_types = {
            # Documents
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'application/vnd.ms-excel': 'xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
            
            # Images
            'image/jpeg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            
            # Audio
            'audio/mpeg': 'mp3',
            'audio/wav': 'wav',
            'audio/wave': 'wav',
            'audio/x-wav': 'wav',
            
            # Video
            'video/mp4': 'mp4',
            'video/mpeg': 'mpeg',
        }
    
    def validate_file(self, uploaded_file) -> dict:
        """
        التحقق من صحة الملف
        
        Returns:
            dict: {'valid': bool, 'error': str or None}
        """
        # التحقق من وجود الملف
        if not uploaded_file:
            return {'valid': False, 'error': 'لم يتم رفع أي ملف'}
        
        # التحقق من اسم الملف
        if not InputValidator.is_safe_filename(uploaded_file.name):
            return {'valid': False, 'error': 'اسم الملف غير آمن'}
        
        # التحقق من الامتداد
        ext = self._get_extension(uploaded_file.name)
        if ext not in self.allowed_extensions:
            return {
                'valid': False,
                'error': f'امتداد الملف غير مسموح. الامتدادات المسموحة: {", ".join(self.allowed_extensions)}'
            }
        
        # التحقق من الحجم
        if uploaded_file.size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            return {'valid': False, 'error': f'حجم الملف كبير جداً. الحد الأقصى: {max_mb:.0f}MB'}
        
        # التحقق من نوع MIME الحقيقي
        mime_result = self._verify_mime_type(uploaded_file)
        if not mime_result['valid']:
            return mime_result
        
        return {'valid': True, 'error': None}
    
    def _get_extension(self, filename: str) -> str:
        """الحصول على امتداد الملف"""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    def _verify_mime_type(self, uploaded_file) -> dict:
        """التحقق من نوع MIME الحقيقي للملف"""
        try:
            # قراءة أول 2048 بايت لتحديد نوع الملف
            uploaded_file.seek(0)
            file_head = uploaded_file.read(2048)
            uploaded_file.seek(0)
            
            # إذا كان magic متاحاً، استخدمه للتحقق المتقدم
            if MAGIC_AVAILABLE:
                try:
                    # استخدام python-magic لتحديد نوع الملف الحقيقي
                    mime = magic.Magic(mime=True)
                    detected_mime = mime.from_buffer(file_head)
                    
                    # التحقق من أن نوع MIME مسموح
                    if detected_mime not in self.allowed_mime_types:
                        return {
                            'valid': False,
                            'error': f'نوع الملف غير مسموح: {detected_mime}'
                        }
                    
                    # التحقق من تطابق الامتداد مع نوع MIME
                    file_ext = self._get_extension(uploaded_file.name)
                    expected_ext = self.allowed_mime_types[detected_mime]
                    
                    if file_ext != expected_ext:
                        return {
                            'valid': False,
                            'error': f'امتداد الملف لا يتطابق مع محتواه'
                        }
                    
                    return {'valid': True, 'error': None}
                except Exception as magic_error:
                    logger.warning(f"Magic MIME detection failed, using basic validation: {str(magic_error)}")
            
            # Fallback: التحقق الأساسي من الامتداد فقط
            # (عندما magic غير متاح أو فشل)
            file_ext = self._get_extension(uploaded_file.name)
            if file_ext in self.allowed_extensions:
                logger.info(f"Using basic MIME validation for: {uploaded_file.name}")
                return {'valid': True, 'error': None}
            else:
                return {
                    'valid': False,
                    'error': f'امتداد الملف غير مسموح: {file_ext}'
                }
            
        except Exception as e:
            logger.error(f"Error verifying MIME type: {str(e)}")
            return {'valid': False, 'error': 'فشل التحقق من نوع الملف'}
    
    def scan_for_viruses(self, uploaded_file) -> dict:
        """
        فحص الملف من الفيروسات
        
        Returns:
            dict: {'is_safe': bool, 'message': str}
        """
        try:
            # قراءة محتوى الملف
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            uploaded_file.seek(0)
            
            # فحص المحتوى
            result = av_scanner.scan_stream(file_content)
            
            return {
                'is_safe': result['is_safe'],
                'message': result['message']
            }
            
        except Exception as e:
            logger.error(f"Error scanning file for viruses: {str(e)}")
            return {
                'is_safe': False,
                'message': f'خطأ في فحص الفيروسات: {str(e)}'
            }
    
    def save_file(self, uploaded_file, subfolder: str = '') -> dict:
        """
        حفظ الملف بشكل آمن
        
        Args:
            uploaded_file: الملف المرفوع
            subfolder: مجلد فرعي لحفظ الملف فيه
            
        Returns:
            dict: {
                'success': bool,
                'file_path': str or None,
                'file_url': str or None,
                'error': str or None
            }
        """
        # التحقق من صحة الملف
        validation = self.validate_file(uploaded_file)
        if not validation['valid']:
            return {
                'success': False,
                'file_path': None,
                'file_url': None,
                'error': validation['error']
            }
        
        # فحص الفيروسات
        virus_scan = self.scan_for_viruses(uploaded_file)
        if not virus_scan['is_safe']:
            return {
                'success': False,
                'file_path': None,
                'file_url': None,
                'error': virus_scan['message']
            }
        
        try:
            # توليد اسم ملف آمن وفريد
            ext = self._get_extension(uploaded_file.name)
            unique_filename = f"{uuid.uuid4()}.{ext}"
            
            # إنشاء المسار الكامل
            upload_dir = Path(settings.MEDIA_ROOT) / subfolder
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / unique_filename
            
            # حفظ الملف
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # إنشاء URL للملف
            relative_path = Path(subfolder) / unique_filename
            file_url = f"{settings.MEDIA_URL}{relative_path.as_posix()}"
            
            logger.info(f"File saved successfully: {file_path}")
            
            return {
                'success': True,
                'file_path': str(file_path),
                'file_url': file_url,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return {
                'success': False,
                'file_path': None,
                'file_url': None,
                'error': f'فشل حفظ الملف: {str(e)}'
            }
    
    def delete_file(self, file_path: str) -> bool:
        """حذف ملف"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False


# إنشاء نسخة واحدة من SecureFileUpload
secure_upload = SecureFileUpload()
