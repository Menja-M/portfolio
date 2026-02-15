# Generated manually for model updates

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Rename sended_at to sent_at
        migrations.RenameField(
            model_name='message',
            old_name='sended_at',
            new_name='sent_at',
        ),
        # Add new fields to Conversation
        migrations.AddField(
            model_name='conversation',
            name='is_read_by_admin',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='is_read_by_user',
            field=models.BooleanField(default=True),
        ),
        # Change user field from ForeignKey to OneToOneField
        migrations.AlterField(
            model_name='conversation',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='conversation',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]