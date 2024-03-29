# Generated by Django 4.0.6 on 2022-08-01 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TabCenterApp', '0002_alter_tournament_entries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='member1_grade',
            field=models.IntegerField(null=True, verbose_name='grade1'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='member2_grade',
            field=models.IntegerField(null=True, verbose_name='grade2'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='member3_grade',
            field=models.IntegerField(null=True, verbose_name='grade3'),
        ),
    ]
