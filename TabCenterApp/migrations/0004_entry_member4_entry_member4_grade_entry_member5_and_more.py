# Generated by Django 4.0.6 on 2022-08-03 18:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TabCenterApp', '0003_alter_entry_member1_grade_alter_entry_member2_grade_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='member4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_member4', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='entry',
            name='member4_grade',
            field=models.IntegerField(null=True, verbose_name='grade3'),
        ),
        migrations.AddField(
            model_name='entry',
            name='member5',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_member5', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='entry',
            name='member5_grade',
            field=models.IntegerField(null=True, verbose_name='grade3'),
        ),
    ]
