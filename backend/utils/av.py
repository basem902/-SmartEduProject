"""
نظام فحص الفيروسات باستخدام ClamAV
"""
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import pyclamd
    CLAMAV_AVAILABLE = True
except ImportError:
    CLAMAV_AVAILABLE = False
    logger.warning("pyclamd not installed. Antivirus scanning disabled.")


class AntivirusScanner:
    """فحص الملفات من الفيروسات"""
    
    def __init__(self):
        self.cd = None
        if CLAMAV_AVAILABLE:
            try:
                # محاولة الاتصال بـ ClamAV
                self.cd = pyclamd.ClamdNetworkSocket(
                    host=settings.CLAMAV_HOST,
                    port=settings.CLAMAV_PORT,
                    timeout=30
                )
                # اختبار الاتصال
                if not self.cd.ping():
                    logger.warning("ClamAV daemon is not responding")
                    self.cd = None
            except Exception as e:
                logger.warning(f"Cannot connect to ClamAV: {str(e)}")
                self.cd = None
    
    def is_available(self) -> bool:
        """التحقق من توفر ClamAV"""
        return self.cd is not None
    
    def scan_file(self, file_path: str) -> dict:
        """
        فحص ملف من الفيروسات
        
        Returns:
            dict: {'is_safe': bool, 'virus_name': str or None, 'message': str}
        """
        if not os.path.exists(file_path):
            return {
                'is_safe': False,
                'virus_name': None,
                'message': 'الملف غير موجود'
            }
        
        # إذا لم يكن ClamAV متوفراً، نتحقق فقط من حجم الملف
        if not self.is_available():
            file_size = os.path.getsize(file_path)
            if file_size > settings.MAX_UPLOAD_SIZE:
                return {
                    'is_safe': False,
                    'virus_name': None,
                    'message': 'حجم الملف كبير جداً'
                }
            logger.warning("ClamAV not available - skipping virus scan")
            return {
                'is_safe': True,
                'virus_name': None,
                'message': 'تم قبول الملف (ClamAV غير متوفر)'
            }
        
        try:
            # فحص الملف
            result = self.cd.scan_file(file_path)
            
            if result is None:
                # لم يتم العثور على فيروس
                return {
                    'is_safe': True,
                    'virus_name': None,
                    'message': 'الملف آمن'
                }
            
            # تم العثور على فيروس
            file_name = list(result.keys())[0]
            status, virus_name = result[file_name]
            
            return {
                'is_safe': False,
                'virus_name': virus_name,
                'message': f'تم اكتشاف فيروس: {virus_name}'
            }
            
        except Exception as e:
            logger.error(f"Error scanning file: {str(e)}")
            return {
                'is_safe': False,
                'virus_name': None,
                'message': f'خطأ في الفحص: {str(e)}'
            }
    
    def scan_stream(self, file_content: bytes) -> dict:
        """
        فحص محتوى ملف من الفيروسات
        
        Args:
            file_content: محتوى الملف كـ bytes
            
        Returns:
            dict: {'is_safe': bool, 'virus_name': str or None, 'message': str}
        """
        if not self.is_available():
            logger.warning("ClamAV not available - skipping virus scan")
            return {
                'is_safe': True,
                'virus_name': None,
                'message': 'تم قبول الملف (ClamAV غير متوفر)'
            }
        
        try:
            result = self.cd.scan_stream(file_content)
            
            if result is None:
                return {
                    'is_safe': True,
                    'virus_name': None,
                    'message': 'الملف آمن'
                }
            
            status, virus_name = result['stream']
            
            return {
                'is_safe': False,
                'virus_name': virus_name,
                'message': f'تم اكتشاف فيروس: {virus_name}'
            }
            
        except Exception as e:
            logger.error(f"Error scanning stream: {str(e)}")
            return {
                'is_safe': False,
                'virus_name': None,
                'message': f'خطأ في الفحص: {str(e)}'
            }
    
    def get_version(self) -> str:
        """الحصول على إصدار ClamAV"""
        if not self.is_available():
            return "غير متوفر"
        
        try:
            return self.cd.version()
        except Exception:
            return "غير معروف"


# إنشاء نسخة واحدة من Scanner
av_scanner = AntivirusScanner()
