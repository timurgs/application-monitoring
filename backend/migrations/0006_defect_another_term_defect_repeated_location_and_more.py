# Generated by Django 4.1.2 on 2022-11-05 22:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_alter_request_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='defect',
            name='another_term',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Повторный срок'),
        ),
        migrations.AddField(
            model_name='defect',
            name='repeated_location',
            field=models.CharField(blank=True, max_length=13, verbose_name='Повторная локация'),
        ),
        migrations.AlterField(
            model_name='request',
            name='implementing_organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='backend.implementingorganization', verbose_name='Организация-исполнитель'),
        ),
    ]