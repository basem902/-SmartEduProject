"""
New Serializers for Project Creation
"""
from rest_framework import serializers
from .models import Project, ProjectFile, Submission
from apps.sections.models import Section
from .validators import SUPPORTED_FILE_TYPES, validate_file_type


class ProjectFileSerializer(serializers.ModelSerializer):
    """Serializer for project files"""
    
    class Meta:
        model = ProjectFile
        fields = ['id', 'file_type', 'file_path', 'file_name', 'file_size', 'external_link', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ProjectCreateSerializer(serializers.Serializer):
    """Serializer for creating projects"""
    
    # Basic Info
    title = serializers.CharField(max_length=200)
    subject = serializers.ChoiceField(choices=['المهارات الرقمية', 'العلوم', 'رياضيات'])
    description = serializers.CharField(required=False, allow_blank=True)
    
    # Target
    grade_id = serializers.IntegerField()
    section_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    
    # Instructions
    instructions = serializers.CharField(required=False, allow_blank=True)
    requirements = serializers.CharField(required=False, allow_blank=True)
    tips = serializers.CharField(required=False, allow_blank=True)
    
    # Settings
    allowed_file_types = serializers.ListField(
        child=serializers.CharField(),
        min_length=1
    )
    max_file_size = serializers.IntegerField(min_value=1, max_value=100)
    max_grade = serializers.IntegerField(min_value=1, max_value=100)
    start_date = serializers.DateTimeField()
    deadline = serializers.DateTimeField()
    allow_late_submission = serializers.BooleanField(default=False)
    send_reminder = serializers.BooleanField(default=True)
    ai_check_plagiarism = serializers.BooleanField(default=False)
    
    # Files (handled separately as multipart/form-data)
    video_link = serializers.URLField(required=False, allow_blank=True)
    external_links = serializers.ListField(
        child=serializers.URLField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list
    )
    
    def validate_external_links(self, value):
        """Clean external links - remove empty strings"""
        if not value:
            return []
        # Filter out empty or whitespace-only strings
        cleaned = [link.strip() for link in value if link and link.strip()]
        return cleaned
    
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
    
    def validate(self, data):
        # Validate dates
        if data['deadline'] <= data['start_date']:
            raise serializers.ValidationError({
                'deadline': 'الموعد النهائي يجب أن يكون بعد تاريخ البداية'
            })
        
        # Validate sections belong to grade
        grade_id = data['grade_id']
        section_ids = data['section_ids']
        
        sections = Section.objects.filter(
            id__in=section_ids,
            grade_id=grade_id
        )
        
        if sections.count() != len(section_ids):
            raise serializers.ValidationError({
                'section_ids': 'بعض الشُعب غير موجودة أو لا تنتمي للصف المختار'
            })
        
        # Validate max file size based on file types
        allowed_types = data.get('allowed_file_types', [])
        max_file_size = data.get('max_file_size', 10)
        
        # For video files, recommend 50 MB
        if 'video' in allowed_types and max_file_size < 50:
            raise serializers.ValidationError({
                'max_file_size': 'للفيديوهات، يُنصح بحجم 50 MB أو أكثر (لفيديو 30 ثانية بجودة HD)'
            })
        
        return data


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for listing projects"""
    
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    sections_count = serializers.SerializerMethodField()
    submissions_count = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'subject', 'description',
            'teacher_name', 'sections_count', 
            'start_date', 'deadline', 'is_expired', 'days_remaining',
            'max_grade', 'submissions_count',
            'telegram_sent', 'is_active', 'created_at'
        ]
    
    def get_sections_count(self, obj):
        return obj.sections.count()
    
    def get_submissions_count(self, obj):
        return obj.submissions.count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for project details"""
    
    teacher_name = serializers.SerializerMethodField()
    grade_display = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'subject', 'description',
            'teacher_name', 'grade_display', 'sections', 'files',
            'instructions', 'requirements', 'tips',
            'start_date', 'deadline',
            'max_file_size', 'allowed_file_types', 'max_grade',
            'allow_late_submission', 'send_reminder', 'ai_check_plagiarism',
            'telegram_sent', 'is_active', 'ai_enhanced',
            'statistics', 'created_at', 'updated_at'
        ]
    
    def get_teacher_name(self, obj):
        try:
            return obj.teacher.full_name if hasattr(obj.teacher, 'full_name') else obj.teacher.username
        except:
            return 'غير محدد'
    
    def get_grade_display(self, obj):
        try:
            sections = obj.sections.all()
            if sections.exists():
                first_section = sections.first()
                return first_section.grade.display_name if hasattr(first_section, 'grade') else 'غير محدد'
            return 'غير محدد'
        except:
            return 'غير محدد'
    
    def get_sections(self, obj):
        try:
            sections = obj.sections.all()
            return [{
                'id': s.id,
                'name': s.section_name if hasattr(s, 'section_name') else str(s),
                'grade': s.grade.display_name if hasattr(s, 'grade') and hasattr(s.grade, 'display_name') else 'غير محدد',
                'student_count': s.student_count if hasattr(s, 'student_count') else 0
            } for s in sections]
        except Exception as e:
            print(f"Error getting sections: {e}")
            return []
    
    def get_files(self, obj):
        try:
            files = obj.files.all() if hasattr(obj, 'files') else []
            result = []
            for f in files:
                file_data = {
                    'id': f.id,
                    'file_name': f.file_name or 'ملف',
                    'name': f.file_name or 'ملف',  # للتوافقية
                    'file_type': f.file_type or 'unknown',
                    'file_size': f.file_size or 0,
                    'file_path': f.file_path or None,
                    'external_link': f.external_link or None
                }
                result.append(file_data)
                # Debug log
                if f.file_type == 'link':
                    print(f"🔗 Serializing link: {f.external_link or f.file_path}")
            
            print(f"📦 Total files serialized: {len(result)}")
            return result
        except Exception as e:
            print(f"❌ Error getting files: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_statistics(self, obj):
        try:
            sections = obj.sections.all()
            total_students = sum(s.student_count for s in sections if hasattr(s, 'student_count'))
            
            # Check if submissions relation exists
            if hasattr(obj, 'submissions'):
                total_submissions = obj.submissions.count()
                pending = obj.submissions.filter(status='pending').count()
                approved = obj.submissions.filter(status='approved').count()
            else:
                total_submissions = 0
                pending = 0
                approved = 0
            
            return {
                'total_students': total_students,
                'total_submissions': total_submissions,
                'submission_rate': round((total_submissions / total_students * 100) if total_students > 0 else 0, 2),
                'pending_submissions': pending,
                'approved_submissions': approved,
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_students': 0,
                'total_submissions': 0,
                'submission_rate': 0,
                'pending_submissions': 0,
                'approved_submissions': 0,
            }
