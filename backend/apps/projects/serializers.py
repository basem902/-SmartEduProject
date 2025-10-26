"""
Serializers for Projects App
"""
import logging
from rest_framework import serializers
from .models import Project, Student, Group, Submission, ProjectFile
from utils.validation import InputValidator

logger = logging.getLogger(__name__)


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer للمشروع"""
    
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    submissions_count = serializers.SerializerMethodField()
    sections_count = serializers.SerializerMethodField()
    sections_info = serializers.SerializerMethodField()
    grade_display = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'subject', 'start_date', 'deadline',
            'max_file_size', 'allowed_file_types', 'max_grade',
            'instructions', 'requirements', 'tips',
            'is_active', 'created_at', 'updated_at', 
            'teacher_name', 'submissions_count', 'sections_count', 'sections_info',
            'grade_display',  # Display grade from first section
            'allow_late_submission', 'send_reminder', 'ai_check_plagiarism',
            'telegram_sent',  # Show if telegram notification was sent
            'files', 'sections'  # Files and sections details
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_submissions_count(self, obj):
        return obj.submissions.count() if hasattr(obj, 'submissions') else 0
    
    def get_sections_count(self, obj):
        return obj.sections.count()
    
    def get_grade_display(self, obj):
        """Get grade display from first section"""
        try:
            first_section = obj.sections.select_related('grade').first()
            if first_section and first_section.grade:
                level_display = dict(first_section.grade.LEVEL_CHOICES).get(
                    first_section.grade.level, 
                    first_section.grade.level
                )
                return f"{level_display} - الصف {first_section.grade.grade_number}"
            return 'متعدد'  # Multiple grades
        except Exception as e:
            logger.warning(f"Error getting grade_display: {str(e)}")
            return 'غير محدد'
    
    def get_sections_info(self, obj):
        try:
            sections_list = []
            for section in obj.sections.all():
                try:
                    if section.grade:
                        # Get grade display name
                        level_display = dict(section.grade.LEVEL_CHOICES).get(section.grade.level, section.grade.level)
                        grade_display = f"{level_display} - الصف {section.grade.grade_number}"
                    else:
                        grade_display = 'غير محدد'
                except Exception as e:
                    logger.warning(f"Error getting grade for section {section.id}: {str(e)}")
                    grade_display = 'غير محدد'
                
                sections_list.append({
                    'id': section.id,
                    'name': section.section_name,
                    'grade': grade_display
                })
            return sections_list
        except Exception as e:
            logger.error(f"Error getting sections_info: {str(e)}")
            return []
    
    def get_files(self, obj):
        """Get project files including external links"""
        try:
            files = obj.files.all() if hasattr(obj, 'files') else []
            return [{
                'id': f.id,
                'file_name': f.file_name if hasattr(f, 'file_name') else 'ملف',
                'name': f.file_name if hasattr(f, 'file_name') else 'ملف',
                'file_type': f.file_type if hasattr(f, 'file_type') else 'unknown',
                'file_size': f.file_size if hasattr(f, 'file_size') else 0,
                'file_path': f.file_path if hasattr(f, 'file_path') else None,
                'external_link': f.external_link if hasattr(f, 'external_link') else None
            } for f in files]
        except Exception as e:
            logger.error(f"Error getting files: {str(e)}")
            return []
    
    def get_sections(self, obj):
        """Get detailed sections info for preview modal"""
        try:
            sections_list = []
            for section in obj.sections.select_related('grade').all():
                sections_list.append({
                    'id': section.id,
                    'name': section.section_name,
                    'student_count': section.student_count if hasattr(section, 'student_count') else 0
                })
            return sections_list
        except Exception as e:
            logger.error(f"Error getting sections: {str(e)}")
            return []
    
    def validate_title(self, value):
        return InputValidator.validate_text(value, min_length=3, max_length=200, field_name="عنوان المشروع")
    
    def validate_description(self, value):
        if value:
            return InputValidator.validate_text(value, min_length=10, max_length=5000, field_name="وصف المشروع")
        return value
    
    def validate_subject(self, value):
        return InputValidator.validate_text(value, min_length=2, max_length=100, field_name="المادة")


class StudentSerializer(serializers.ModelSerializer):
    """Serializer للطالب"""
    
    class Meta:
        model = Student
        fields = ['id', 'student_name', 'student_id', 'phone', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_student_name(self, value):
        return InputValidator.validate_name(value, "اسم الطالب")
    
    def validate_student_id(self, value):
        return InputValidator.validate_text(value, min_length=1, max_length=50, field_name="رقم الطالب")
    
    def validate_phone(self, value):
        if value:
            return InputValidator.validate_phone(value)
        return value
    
    def validate_email(self, value):
        if value:
            return InputValidator.validate_email(value)
        return value


class GroupSerializer(serializers.ModelSerializer):
    """Serializer للمجموعة"""
    
    students = StudentSerializer(many=True, read_only=True)
    student_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Group
        fields = ['id', 'group_name', 'students', 'student_ids', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_group_name(self, value):
        return InputValidator.validate_text(value, min_length=2, max_length=100, field_name="اسم المجموعة")


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer للتسليم"""
    
    project_title = serializers.CharField(source='project.title', read_only=True)
    student_name = serializers.CharField(source='student.student_name', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.group_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'project', 'group', 'student', 'file_path', 'file_name',
            'file_size', 'file_type', 'status', 'notes', 'grade',
            'submitted_at', 'reviewed_at', 'project_title', 'student_name', 'group_name'
        ]
        read_only_fields = ['id', 'file_path', 'file_size', 'file_type', 'submitted_at']


class SubmissionReviewSerializer(serializers.Serializer):
    """Serializer لمراجعة التسليم"""
    
    status = serializers.ChoiceField(choices=['approved', 'rejected'])
    notes = serializers.CharField(required=False, allow_blank=True)
    grade = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    
    def validate_notes(self, value):
        if value:
            return InputValidator.validate_text(value, min_length=1, max_length=5000, field_name="الملاحظات")
        return value
