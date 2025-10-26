"""
Serializers for Sections App
"""
from rest_framework import serializers
from .models import SchoolGrade, Section, SectionLink, StudentRegistration, AIGeneratedContent, TelegramGroup, TeacherSubject
from apps.accounts.models import Teacher


class SchoolGradeSerializer(serializers.ModelSerializer):
    """Serializer للصف الدراسي"""
    
    display_name = serializers.ReadOnlyField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    sections_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolGrade
        fields = [
            'id', 'teacher', 'level', 'level_display', 'grade_number',
            'school_name', 'display_name', 'sections_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']
    
    def get_sections_count(self, obj):
        return obj.sections.filter(is_active=True).count()


class SectionLinkSerializer(serializers.ModelSerializer):
    """Serializer لروابط الشُعب"""
    
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    is_expired_status = serializers.SerializerMethodField()
    join_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SectionLink
        fields = [
            'id', 'section', 'platform', 'platform_display',
            'whatsapp_link', 'telegram_link', 'join_token', 'join_link',
            'expires_at', 'is_active', 'is_expired_status',
            'view_count', 'join_count', 'join_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'join_token', 'join_link', 'view_count', 'join_count', 'created_at', 'updated_at']
    
    def get_is_expired_status(self, obj):
        return obj.is_expired()
    
    def get_join_rate(self, obj):
        if obj.view_count == 0:
            return 0
        return round((obj.join_count / obj.view_count) * 100, 2)


class StudentRegistrationSerializer(serializers.ModelSerializer):
    """Serializer لتسجيل الطلاب"""
    
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    grade_display = serializers.CharField(source='grade.display_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    
    class Meta:
        model = StudentRegistration
        fields = [
            'id', 'full_name', 'normalized_name',
            'teacher', 'teacher_name', 'school_name',
            'grade', 'grade_display', 'section', 'section_name',
            'telegram_group', 'telegram_invite_link',
            'registration_ip', 'user_agent',
            'joined_telegram', 'joined_at',
            'is_duplicate', 'original_name',
            'registered_at'
        ]
        read_only_fields = ['id', 'normalized_name', 'registered_at', 'joined_at']


class SectionSerializer(serializers.ModelSerializer):
    """Serializer للشعبة"""
    
    grade_display = serializers.CharField(source='grade.display_name', read_only=True)
    link = SectionLinkSerializer(read_only=True, allow_null=True)
    registrations_count = serializers.SerializerMethodField()
    joined_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Section
        fields = [
            'id', 'grade', 'grade_display', 'section_number', 'section_name',
            'total_students', 'registrations_count', 'joined_count',
            'link', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_students', 'created_at', 'updated_at']
    
    def get_registrations_count(self, obj):
        """عدد الطلاب المسجلين"""
        return obj.registered_students.count() if hasattr(obj, 'registered_students') else 0
    
    def get_joined_count(self, obj):
        """عدد الطلاب الذين انضموا للقروب"""
        return obj.registered_students.filter(joined_telegram=True).count() if hasattr(obj, 'registered_students') else 0


class SectionDetailSerializer(SectionSerializer):
    """Serializer تفصيلي للشعبة مع الطلاب"""
    
    registered_students = StudentRegistrationSerializer(many=True, read_only=True)
    
    class Meta(SectionSerializer.Meta):
        fields = SectionSerializer.Meta.fields + ['registered_students']


class AIGeneratedContentSerializer(serializers.ModelSerializer):
    """Serializer للمحتوى المولد بالـ AI"""
    
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    
    class Meta:
        model = AIGeneratedContent
        fields = [
            'id', 'teacher', 'content_type', 'content_type_display',
            'generated_text', 'is_custom', 'prompt_used', 'model_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher', 'created_at', 'updated_at']


# Serializers للإدخال (Input)

class GradeSetupSerializer(serializers.Serializer):
    """Serializer لإعداد الصف"""
    
    level = serializers.ChoiceField(choices=SchoolGrade.LEVEL_CHOICES)
    grade_number = serializers.IntegerField(min_value=1, max_value=6)
    school_name = serializers.CharField(max_length=200)
    subject = serializers.CharField(max_length=100, required=False, allow_blank=True)  # المادة الدراسية
    sections_count = serializers.IntegerField(min_value=1, max_value=20, required=False)
    sections_list = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False,
        allow_empty=False,
        max_length=50
    )
    
    def validate(self, data):
        # التحقق من رقم الصف حسب المرحلة
        level = data['level']
        grade_number = data['grade_number']
        
        max_grades = {
            'elementary': 6,
            'middle': 3,
            'high': 3,
        }
        
        if grade_number > max_grades[level]:
            raise serializers.ValidationError(
                f"رقم الصف غير صحيح للمرحلة {dict(SchoolGrade.LEVEL_CHOICES)[level]}"
            )
        
        # يجب توفير إما sections_count أو sections_list
        if not data.get('sections_count') and not data.get('sections_list'):
            raise serializers.ValidationError(
                "يجب توفير إما sections_count أو sections_list"
            )
        
        return data


class SectionLinkSetupSerializer(serializers.Serializer):
    """Serializer لإعداد روابط الشعبة"""
    
    section_id = serializers.IntegerField()
    platform = serializers.ChoiceField(choices=SectionLink.PLATFORM_CHOICES)
    whatsapp_link = serializers.URLField(required=False, allow_blank=True)
    telegram_link = serializers.URLField(required=False, allow_blank=True)
    chat_id = serializers.IntegerField(required=False, allow_null=True)  # ✅ إضافة chat_id
    
    def validate(self, data):
        platform = data['platform']
        whatsapp = data.get('whatsapp_link')
        telegram = data.get('telegram_link')
        
        # التحقق من وجود الروابط المطلوبة
        if platform == 'whatsapp' and not whatsapp:
            raise serializers.ValidationError("رابط واتساب مطلوب")
        elif platform == 'telegram' and not telegram:
            raise serializers.ValidationError("رابط تيليجرام مطلوب")
        elif platform == 'both' and (not whatsapp or not telegram):
            raise serializers.ValidationError("كلا الرابطين مطلوب")
        
        # التحقق من صحة رابط واتساب
        if whatsapp and 'chat.whatsapp.com' not in whatsapp and 'wa.me' not in whatsapp:
            raise serializers.ValidationError("رابط واتساب غير صحيح")
        
        # التحقق من صحة رابط تيليجرام
        if telegram and 't.me' not in telegram:
            raise serializers.ValidationError("رابط تيليجرام غير صحيح")
        
        return data


class StudentJoinSerializer(serializers.Serializer):
    """Serializer لتسجيل الطالب عبر الرابط"""
    
    full_name = serializers.CharField(max_length=100)
    token = serializers.CharField(max_length=64)
    
    def validate_full_name(self, value):
        # تنظيف الاسم
        value = value.strip()
        
        # التحقق من الطول
        if len(value) < 3:
            raise serializers.ValidationError("الاسم قصير جداً")
        
        # التحقق من وجود أحرف
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError("الاسم يجب أن يحتوي على أحرف")
        
        return value


class AIGenerateSerializer(serializers.Serializer):
    """Serializer لطلب توليد محتوى AI"""
    
    content_type = serializers.ChoiceField(choices=AIGeneratedContent.CONTENT_TYPES)
    context = serializers.DictField(required=False, help_text="معلومات إضافية للـ prompt")
    
    # معلومات السياق المحتملة
    school_name = serializers.CharField(max_length=200, required=False)
    grade_level = serializers.CharField(max_length=20, required=False)
    grade_number = serializers.IntegerField(required=False)
    section_name = serializers.CharField(max_length=50, required=False)


class TelegramGroupSerializer(serializers.ModelSerializer):
    """Serializer لقروبات تيليجرام"""
    
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    grade_display = serializers.CharField(source='section.grade.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_fully_configured = serializers.ReadOnlyField()
    
    class Meta:
        model = TelegramGroup
        fields = [
            'id', 'section', 'section_name', 'grade_display',
            'group_name', 'chat_id', 'invite_link',
            'bot_username', 'is_bot_added', 'is_bot_admin', 'bot_permissions',
            'permissions_applied', 'read_only_mode',
            'instructions_message_id', 'instructions_sent', 'instructions_pinned',
            'status', 'status_display', 'error_message',
            'members_count', 'messages_sent', 'last_message_at',
            'created_by_phone', 'creation_metadata',
            'is_fully_configured',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateTelegramGroupsSerializer(serializers.Serializer):
    """Serializer لطلب إنشاء قروبات تيليجرام"""
    
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        help_text="رقم الهاتف المسجل في تيليجرام (مع كود الدولة)"
    )
    
    def validate_phone_number(self, value):
        """التحقق من صيغة رقم الهاتف"""
        value = value.strip()
        if not value.startswith('+'):
            raise serializers.ValidationError("رقم الهاتف يجب أن يبدأ بـ + متبوعاً بكود الدولة")
        
        # إزالة + والتحقق من الأرقام
        digits = value[1:]
        if not digits.isdigit():
            raise serializers.ValidationError("رقم الهاتف يجب أن يحتوي على أرقام فقط")
        
        if len(digits) < 10 or len(digits) > 15:
            raise serializers.ValidationError("طول رقم الهاتف غير صحيح")
        
        return value


# ==================== Student Registration Serializers ====================

class StudentRegistrationSerializer(serializers.Serializer):
    """Serializer لتسجيل الطلاب"""
    
    full_name = serializers.CharField(
        max_length=200,
        min_length=6,
        required=True,
        help_text="الاسم الكامل (على الأقل اسمين)"
    )
    grade_id = serializers.IntegerField(required=True)
    section_id = serializers.IntegerField(required=True)
    
    def validate_full_name(self, value):
        """التحقق من الاسم"""
        value = value.strip()
        
        # يجب أن يحتوي على مسافة واحدة على الأقل (اسمين)
        if ' ' not in value:
            raise serializers.ValidationError("يرجى إدخال الاسم الكامل (اسمين على الأقل)")
        
        # التحقق من أن الاسم عربي أو إنجليزي فقط
        import re
        if not re.match(r'^[\u0600-\u06FFa-zA-Z\s]+$', value):
            raise serializers.ValidationError("الاسم يجب أن يحتوي على أحرف عربية أو إنجليزية فقط")
        
        return value


class StudentRegistrationResponseSerializer(serializers.Serializer):
    """Serializer للرد على تسجيل الطالب"""
    
    name = serializers.CharField()
    grade = serializers.CharField()
    section = serializers.CharField()


class TeacherJoinLinkSerializer(serializers.Serializer):
    """Serializer لرابط انضمام المعلم"""
    
    join_url = serializers.CharField()
    full_url = serializers.CharField()
    views_count = serializers.IntegerField()
    registrations_count = serializers.IntegerField()


class TeacherInfoSerializer(serializers.Serializer):
    """Serializer لمعلومات المعلم في صفحة الانضمام"""
    
    name = serializers.CharField()
    school = serializers.CharField()
    subject = serializers.CharField()


class SectionSimpleSerializer(serializers.Serializer):
    """Serializer بسيط للشعبة"""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    has_telegram = serializers.BooleanField()


class GradeWithSectionsSerializer(serializers.Serializer):
    """Serializer للصف مع شُعبه"""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    sections = SectionSimpleSerializer(many=True)


class TeacherSubjectSerializer(serializers.ModelSerializer):
    """Serializer لمواد المعلم"""
    
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    grade_name = serializers.CharField(source='grade.display_name', read_only=True)
    section_name = serializers.CharField(source='section.section_name', read_only=True)
    
    class Meta:
        model = TeacherSubject
        fields = [
            'id', 'teacher', 'teacher_name', 'teacher_phone',
            'subject_name', 'grade', 'grade_name',
            'section', 'section_name', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'teacher_phone', 'created_at', 'updated_at']


class AssignSubjectsSerializer(serializers.Serializer):
    """Serializer لتعيين المواد للشُعب"""
    
    grade_id = serializers.IntegerField()
    section_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='قائمة IDs الشُعب'
    )
    subject_names = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        help_text='قائمة أسماء المواد'
    )
    
    def validate(self, data):
        """التحقق من البيانات"""
        # التحقق من وجود الصف
        try:
            grade = SchoolGrade.objects.get(id=data['grade_id'])
        except SchoolGrade.DoesNotExist:
            raise serializers.ValidationError({'grade_id': 'الصف غير موجود'})
        
        # التحقق من الشُعب
        sections = Section.objects.filter(
            id__in=data['section_ids'],
            grade=grade
        )
        
        if sections.count() != len(data['section_ids']):
            raise serializers.ValidationError({'section_ids': 'بعض الشُعب غير موجودة أو لا تنتمي لهذا الصف'})
        
        data['grade'] = grade
        data['sections'] = list(sections)
        
        return data
