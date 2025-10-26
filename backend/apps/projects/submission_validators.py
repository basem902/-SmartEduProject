"""
Submission File Validators
"""
import os
from django.core.exceptions import ValidationError
from .validators import (
    SUPPORTED_FILE_TYPES,
    validate_file_type,
    validate_file_size,
    get_allowed_extensions
)


def validate_submission_file(file_obj, project):
    """
    Comprehensive validation for submission files
    
    Args:
        file_obj: Uploaded file object
        project: Project instance
    
    Returns:
        dict: Validation result with errors if any
    
    Raises:
        ValidationError: If file is invalid
    """
    errors = []
    
    # 1. Get file info
    file_name = file_obj.name
    file_size = file_obj.size
    file_extension = os.path.splitext(file_name)[1].lower()
    
    # 2. Validate file type
    allowed_types = project.allowed_file_types
    is_valid_type, type_error = validate_file_type(file_extension, allowed_types)
    
    if not is_valid_type:
        errors.append(type_error)
    
    # 3. Validate file size
    max_size_mb = project.max_file_size
    is_valid_size, size_error = validate_file_size(file_size, max_size_mb)
    
    if not is_valid_size:
        errors.append(size_error)
    
    # 4. Special validation for video files
    if 'video' in allowed_types and file_extension in SUPPORTED_FILE_TYPES['video']['extensions']:
        # Video-specific validation
        file_size_mb = file_size / (1024 * 1024)
        
        # Warn if video is too large for 30 seconds
        if file_size_mb > 50:
            errors.append(
                f'⚠️ تحذير: حجم الفيديو ({file_size_mb:.1f} MB) كبير جداً لفيديو 30 ثانية. '
                'تأكد من أن مدة الفيديو لا تتجاوز 30 ثانية.'
            )
        
        # Estimate duration (rough estimate: 1 MB = ~1 second for HD video)
        estimated_duration = file_size_mb * 0.6  # More accurate estimate
        if estimated_duration > 35:
            errors.append(
                f'⚠️ تحذير: حجم الفيديو يشير إلى أن مدته قد تتجاوز 30 ثانية. '
                f'الحجم المتوقع لفيديو 30 ثانية HD: ~30-50 MB'
            )
    
    # 5. Special validation for audio files
    if 'audio' in allowed_types and file_extension in SUPPORTED_FILE_TYPES['audio']['extensions']:
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size_mb > 20:
            errors.append(
                f'⚠️ تحذير: حجم الملف الصوتي ({file_size_mb:.1f} MB) كبير جداً. '
                'تأكد من جودة الصوت المناسبة.'
            )
    
    # 6. Check file name
    if len(file_name) > 255:
        errors.append('اسم الملف طويل جداً (الحد الأقصى: 255 حرف)')
    
    if errors:
        raise ValidationError(errors)
    
    return {
        'valid': True,
        'file_name': file_name,
        'file_size': file_size,
        'file_extension': file_extension,
        'file_type': get_file_type_from_extension(file_extension, allowed_types)
    }


def get_file_type_from_extension(extension, allowed_types):
    """
    Get file type code from extension
    
    Args:
        extension (str): File extension (e.g., '.mp4')
        allowed_types (list): List of allowed file types
    
    Returns:
        str: File type code (e.g., 'video')
    """
    for file_type in allowed_types:
        if file_type in SUPPORTED_FILE_TYPES:
            if extension in SUPPORTED_FILE_TYPES[file_type]['extensions']:
                return file_type
    
    return 'unknown'


def get_submission_requirements_text(project):
    """
    Generate human-readable requirements text for students
    
    Args:
        project: Project instance
    
    Returns:
        str: Formatted requirements text
    """
    allowed_types = project.allowed_file_types
    max_size = project.max_file_size
    
    # Get extensions
    extensions = get_allowed_extensions(allowed_types)
    
    # Format file types
    type_labels = []
    for file_type in allowed_types:
        if file_type in SUPPORTED_FILE_TYPES:
            type_labels.append(SUPPORTED_FILE_TYPES[file_type]['label'])
    
    requirements = f"""
📋 **متطلبات رفع الملف:**

📁 **أنواع الملفات المسموحة:**
   {', '.join(type_labels)}
   ({', '.join(extensions)})

📏 **الحد الأقصى للحجم:** {max_size} MB

"""
    
    # Add special notes for video
    if 'video' in allowed_types:
        requirements += """
🎬 **ملاحظات مهمة للفيديو:**
   • المدة: 30 ثانية بالضبط
   • الجودة: HD 1080p
   • الصيغة الموصى بها: MP4
   • آخر 5 ثوانٍ: اسمك الرباعي + الصف + الشعبة

"""
    
    # Add special notes for audio
    if 'audio' in allowed_types:
        requirements += """
🎵 **ملاحظات مهمة للصوت:**
   • جودة صوت واضحة
   • الصيغة الموصى بها: MP3
   • تجنب الضوضاء الخلفية

"""
    
    return requirements.strip()
