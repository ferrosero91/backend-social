# Generated migration for interview questions support
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_role'),
    ]

    operations = [
        # Add unique constraint for interview questions order
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(
                fields=['interview', 'order'],
                name='unique_interview_question_order'
            ),
        ),
        # Add index for faster question lookups
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['interview', 'order'], name='idx_question_interview_order'),
        ),
    ]
