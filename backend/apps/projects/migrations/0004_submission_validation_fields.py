# Generated migration for submission validation fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_project_ai_enhanced_project_instructions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='file_hash',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Hash الملف'),
        ),
        migrations.AddField(
            model_name='submission',
            name='validation_data',
            field=models.JSONField(blank=True, null=True, verbose_name='بيانات التحقق'),
        ),
        migrations.AddField(
            model_name='submission',
            name='virus_scanned',
            field=models.BooleanField(default=False, verbose_name='تم فحص الفيروسات'),
        ),
        migrations.AddField(
            model_name='submission',
            name='virus_clean',
            field=models.BooleanField(default=True, verbose_name='خالي من الفيروسات'),
        ),
        migrations.AddField(
            model_name='submission',
            name='ai_checked',
            field=models.BooleanField(default=False, verbose_name='تم الفحص بالذكاء الاصطناعي'),
        ),
        migrations.AddField(
            model_name='submission',
            name='ai_compliant',
            field=models.BooleanField(default=True, verbose_name='متوافق مع المتطلبات'),
        ),
        migrations.AddField(
            model_name='submission',
            name='ai_confidence',
            field=models.IntegerField(default=0, verbose_name='مستوى الثقة'),
        ),
    ]
