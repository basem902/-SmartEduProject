"""
File Type Validators for Projects App
"""

# ✅ Supported file types and extensions
SUPPORTED_FILE_TYPES = {
    'pdf': {
        'extensions': ['.pdf'],
        'mime_types': ['application/pdf'],
        'max_size_mb': 50,
        'label': 'PDF'
    },
    'doc': {
        'extensions': ['.doc', '.docx'],
        'mime_types': [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ],
        'max_size_mb': 50,
        'label': 'Word'
    },
    'ppt': {
        'extensions': ['.ppt', '.pptx'],
        'mime_types': [
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ],
        'max_size_mb': 50,
        'label': 'PowerPoint'
    },
    'xls': {
        'extensions': ['.xls', '.xlsx'],
        'mime_types': [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        'max_size_mb': 50,
        'label': 'Excel'
    },
    'img': {
        'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
        'mime_types': [
            'image/jpeg',
            'image/png',
            'image/gif',
            'image/bmp',
            'image/webp',
            'image/svg+xml'
        ],
        'max_size_mb': 20,
        'label': 'صور'
    },
    'video': {
        'extensions': ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.m4v'],
        'mime_types': [
            'video/mp4',
            'video/x-msvideo',
            'video/quicktime',
            'video/x-ms-wmv',
            'video/x-matroska',
            'video/x-flv',
            'video/webm',
            'video/x-m4v'
        ],
        'max_size_mb': 50,  # 50 MB for 30-second HD video
        'label': 'فيديو',
        'description': 'فيديوهات بجودة HD (30 ثانية أو أقل - حجم أقصى 50 MB)'
    },
    'audio': {
        'extensions': ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.wma', '.flac'],
        'mime_types': [
            'audio/mpeg',
            'audio/wav',
            'audio/x-m4a',
            'audio/aac',
            'audio/ogg',
            'audio/x-ms-wma',
            'audio/flac'
        ],
        'max_size_mb': 20,
        'label': 'صوت'
    },
    'zip': {
        'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'mime_types': [
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
            'application/x-tar',
            'application/gzip'
        ],
        'max_size_mb': 100,
        'label': 'ملفات مضغوطة'
    }
}


def get_allowed_extensions(file_types):
    """
    Get list of allowed file extensions based on file types
    
    Args:
        file_types (list): List of file type codes (e.g., ['pdf', 'video'])
    
    Returns:
        list: List of allowed extensions (e.g., ['.pdf', '.mp4', '.avi'])
    """
    extensions = []
    for file_type in file_types:
        if file_type in SUPPORTED_FILE_TYPES:
            extensions.extend(SUPPORTED_FILE_TYPES[file_type]['extensions'])
    return extensions


def get_max_file_size(file_types):
    """
    Get maximum file size for the given file types
    
    Args:
        file_types (list): List of file type codes
    
    Returns:
        int: Maximum file size in MB
    """
    max_size = 10  # Default
    for file_type in file_types:
        if file_type in SUPPORTED_FILE_TYPES:
            type_max = SUPPORTED_FILE_TYPES[file_type]['max_size_mb']
            max_size = max(max_size, type_max)
    return max_size


def validate_file_type(file_extension, allowed_types):
    """
    Validate if file extension is allowed
    
    Args:
        file_extension (str): File extension (e.g., '.mp4')
        allowed_types (list): List of allowed file type codes
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file_extension.startswith('.'):
        file_extension = f'.{file_extension}'
    
    file_extension = file_extension.lower()
    allowed_extensions = get_allowed_extensions(allowed_types)
    
    if file_extension in allowed_extensions:
        return True, None
    
    return False, f'نوع الملف {file_extension} غير مسموح. الأنواع المسموحة: {", ".join(allowed_extensions)}'


def validate_file_size(file_size_bytes, max_size_mb):
    """
    Validate if file size is within limits
    
    Args:
        file_size_bytes (int): File size in bytes
        max_size_mb (int): Maximum allowed size in MB
    
    Returns:
        tuple: (is_valid, error_message)
    """
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    if file_size_mb <= max_size_mb:
        return True, None
    
    return False, f'حجم الملف ({file_size_mb:.2f} MB) يتجاوز الحد الأقصى المسموح ({max_size_mb} MB)'


def validate_video_duration(file_path, max_duration_seconds=30):
    """
    Validate video duration (optional - requires moviepy or ffmpeg)
    
    Args:
        file_path (str): Path to video file
        max_duration_seconds (int): Maximum duration in seconds
    
    Returns:
        tuple: (is_valid, error_message, duration)
    """
    try:
        # This requires moviepy or ffmpeg-python
        # Uncomment if you want to implement video duration checking
        """
        from moviepy.editor import VideoFileClip
        
        clip = VideoFileClip(file_path)
        duration = clip.duration
        clip.close()
        
        if duration <= max_duration_seconds:
            return True, None, duration
        
        return False, f'مدة الفيديو ({duration:.1f} ثانية) تتجاوز الحد الأقصى ({max_duration_seconds} ثانية)', duration
        """
        return True, None, 0
    except Exception as e:
        return True, None, 0  # Don't fail validation if we can't check duration


def get_file_info(file_types):
    """
    Get formatted information about allowed file types
    
    Args:
        file_types (list): List of file type codes
    
    Returns:
        dict: Information about file types
    """
    info = {
        'types': [],
        'extensions': [],
        'max_size_mb': 10,
        'descriptions': []
    }
    
    for file_type in file_types:
        if file_type in SUPPORTED_FILE_TYPES:
            type_info = SUPPORTED_FILE_TYPES[file_type]
            info['types'].append(type_info['label'])
            info['extensions'].extend(type_info['extensions'])
            info['max_size_mb'] = max(info['max_size_mb'], type_info['max_size_mb'])
            
            if 'description' in type_info:
                info['descriptions'].append(type_info['description'])
    
    return info
