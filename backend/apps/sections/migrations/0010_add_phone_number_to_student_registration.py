# Generated manually to fix phone_number field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0009_add_telegram_fields_to_student_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentregistration',
            name='phone_number',
            field=models.CharField(
                max_length=15,
                blank=True,
                null=True,
                verbose_name='رقم الجوال',
                help_text='رقم جوال الطالب للتواصل'
            ),
        ),
    ]
