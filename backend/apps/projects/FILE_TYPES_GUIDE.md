# 📋 دليل أنواع الملفات المدعومة

## 🎯 الأنواع المدعومة

### 1. PDF (pdf)
- **الصيغ**: `.pdf`
- **الحد الأقصى**: 50 MB
- **الاستخدام**: المستندات والتقارير

### 2. Word (doc)
- **الصيغ**: `.doc`, `.docx`
- **الحد الأقصى**: 50 MB
- **الاستخدام**: المستندات النصية

### 3. PowerPoint (ppt)
- **الصيغ**: `.ppt`, `.pptx`
- **الحد الأقصى**: 50 MB
- **الاستخدام**: العروض التقديمية

### 4. Excel (xls)
- **الصيغ**: `.xls`, `.xlsx`
- **الحد الأقصى**: 50 MB
- **الاستخدام**: الجداول والبيانات

### 5. صور (img)
- **الصيغ**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`
- **الحد الأقصى**: 20 MB
- **الاستخدام**: الصور والرسومات

### 6. 🎬 فيديو (video) ⭐ جديد
- **الصيغ**: `.mp4`, `.avi`, `.mov`, `.wmv`, `.mkv`, `.flv`, `.webm`, `.m4v`
- **الحد الأقصى**: 50 MB
- **الوصف**: فيديوهات بجودة HD (30 ثانية أو أقل)
- **الاستخدام المثالي**: 
  - مشاريع الفيديو التعليمية
  - عروض المشاريع الحكومية
  - التسجيلات التقديمية

**📐 مواصفات الفيديو الموصى بها:**
- المدة: 30 ثانية
- الجودة: HD 1080p (1920x1080)
- الصيغة: MP4
- معدل البت: ~10-15 Mbps
- الحجم المتوقع: 30-50 MB

**✅ مثال على مشروع فيديو:**
```python
project = Project.objects.create(
    title="فيديو عن المشاريع الحكومية",
    allowed_file_types=['video'],
    max_file_size=50,  # 50 MB for 30-second HD video
)
```

### 7. 🎵 صوت (audio) ⭐ جديد
- **الصيغ**: `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`, `.wma`, `.flac`
- **الحد الأقصى**: 20 MB
- **الاستخدام**: 
  - التسجيلات الصوتية
  - البودكاست التعليمي
  - الملفات الصوتية

**📐 مواصفات الصوت الموصى بها:**
- الصيغة: MP3
- معدل البت: 128-192 kbps
- جودة الصوت: واضحة بدون ضوضاء

### 8. ملفات مضغوطة (zip)
- **الصيغ**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`
- **الحد الأقصى**: 100 MB
- **الاستخدام**: ملفات متعددة مضغوطة

---

## 🔧 كيفية الاستخدام في الكود

### 1. Import الـ Validators:
```python
from apps.projects.validators import (
    SUPPORTED_FILE_TYPES,
    validate_file_type,
    validate_file_size,
    get_allowed_extensions,
    get_file_info
)
```

### 2. Validate File Type:
```python
# Check if file extension is allowed
is_valid, error_msg = validate_file_type(
    file_extension='.mp4',
    allowed_types=['video', 'pdf']
)

if not is_valid:
    print(error_msg)
```

### 3. Validate File Size:
```python
# Check if file size is within limits
file_size_bytes = 45 * 1024 * 1024  # 45 MB
max_size_mb = 50

is_valid, error_msg = validate_file_size(
    file_size_bytes=file_size_bytes,
    max_size_mb=max_size_mb
)
```

### 4. Get Allowed Extensions:
```python
# Get list of extensions for file types
allowed_types = ['video', 'audio', 'pdf']
extensions = get_allowed_extensions(allowed_types)
# Returns: ['.mp4', '.avi', '.mov', ..., '.mp3', '.wav', ..., '.pdf']
```

### 5. Get File Info:
```python
# Get detailed information
info = get_file_info(['video', 'audio'])
print(info['types'])        # ['فيديو', 'صوت']
print(info['extensions'])   # ['.mp4', '.avi', ..., '.mp3', '.wav', ...]
print(info['max_size_mb'])  # 50
print(info['descriptions']) # ['فيديوهات بجودة HD...']
```

---

## 📝 Validation في Serializer

تم إضافة validation تلقائي في `ProjectCreateSerializer`:

```python
def validate_allowed_file_types(self, value):
    """Validate allowed file types"""
    if not value:
        raise serializers.ValidationError('يجب اختيار نوع ملف واحد على الأقل')
    
    # Check all file types are supported
    invalid_types = []
    for file_type in value:
        if file_type not in SUPPORTED_FILE_TYPES:
            invalid_types.append(file_type)
    
    if invalid_types:
        raise serializers.ValidationError(
            f'أنواع الملفات التالية غير مدعومة: {", ".join(invalid_types)}'
        )
    
    return value
```

**Validation للفيديو:**
```python
# For video files, recommend 50 MB
if 'video' in allowed_types and max_file_size < 50:
    raise serializers.ValidationError({
        'max_file_size': 'للفيديوهات، يُنصح بحجم 50 MB أو أكثر (لفيديو 30 ثانية بجودة HD)'
    })
```

---

## 🎓 Submission Validation

استخدم `submission_validators.py` للتحقق من ملفات التسليم:

```python
from apps.projects.submission_validators import (
    validate_submission_file,
    get_submission_requirements_text
)

# Validate uploaded file
try:
    result = validate_submission_file(uploaded_file, project)
    print(f"File valid: {result['file_name']}")
except ValidationError as e:
    print(f"Errors: {e.messages}")

# Get requirements text for students
requirements = get_submission_requirements_text(project)
print(requirements)
```

---

## 🎬 مثال كامل: مشروع فيديو عن المشاريع الحكومية

```python
from apps.projects.models import Project
from apps.projects.validators import get_file_info

# Create project
project = Project.objects.create(
    title="فيديو عن المشاريع الحكومية السعودية",
    description="إنشاء فيديو 30 ثانية عن أحد المشاريع الحكومية",
    subject="المهارات الرقمية",
    allowed_file_types=['video'],
    max_file_size=50,
    max_grade=100,
    instructions="""
1. اختر مشروعاً حكومياً (سابك، نيوم، القدية...)
2. أنشئ فيديو 30 ثانية بجودة HD
3. آخر 5 ثوانٍ: اسمك الرباعي + الصف + الشعبة
4. صدّر بصيغة MP4
    """,
    requirements="""
• عمل فردي
• مدة 30 ثانية بالضبط
• جودة HD 1080p
• صيغة MP4
• ممنوع التكرار
    """
)

# Get file info
info = get_file_info(project.allowed_file_types)
print(f"Accepted types: {info['types']}")
print(f"Extensions: {info['extensions']}")
print(f"Max size: {info['max_size_mb']} MB")
```

---

## ⚙️ Configuration

في `settings.py` (اختياري):

```python
# Project file upload settings
PROJECT_FILE_UPLOAD = {
    'MAX_VIDEO_SIZE_MB': 50,  # For 30-second HD video
    'MAX_AUDIO_SIZE_MB': 20,
    'MAX_IMAGE_SIZE_MB': 20,
    'MAX_DOCUMENT_SIZE_MB': 50,
    'VIDEO_DURATION_LIMIT_SECONDS': 30,
}
```

---

## 🚀 الخطوات التالية

### اختياري: إضافة فحص مدة الفيديو

لتفعيل فحص مدة الفيديو، قم بتثبيت:

```bash
pip install moviepy
# أو
pip install ffmpeg-python
```

ثم في `validators.py`:

```python
def validate_video_duration(file_path, max_duration_seconds=30):
    from moviepy.editor import VideoFileClip
    
    clip = VideoFileClip(file_path)
    duration = clip.duration
    clip.close()
    
    if duration <= max_duration_seconds:
        return True, None, duration
    
    return False, f'مدة الفيديو ({duration:.1f}ث) تتجاوز الحد الأقصى ({max_duration_seconds}ث)', duration
```

---

## 📊 ملخص التحديثات

✅ **تم إضافة:**
- دعم ملفات الفيديو (8 صيغ)
- دعم ملفات الصوت (7 صيغ)
- Validation شامل للأحجام والأنواع
- تحذيرات خاصة للفيديو (30 ثانية، 50 MB)
- Documentation كاملة

✅ **الملفات المحدثة:**
- `validators.py` (جديد)
- `submission_validators.py` (جديد)
- `serializers_new.py` (محدّث)
- `FILE_TYPES_GUIDE.md` (جديد)

✅ **الميزات:**
- Validation تلقائي
- رسائل خطأ واضحة بالعربية
- دعم كامل لمشروع الفيديو الحكومي
- توصيات تقنية للحجم والجودة

---

**🎉 الآن النظام جاهز لاستقبال ملفات الفيديو والصوت!**
