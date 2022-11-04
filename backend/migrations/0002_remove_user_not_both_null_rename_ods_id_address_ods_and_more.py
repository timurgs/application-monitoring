# Generated by Django 4.1.2 on 2022-11-04 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='user',
            name='not_both_null',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='ods_id',
            new_name='ods',
        ),
        migrations.RenameField(
            model_name='closingresult',
            old_name='marm_executor_id',
            new_name='marm_executor',
        ),
        migrations.RenameField(
            model_name='closingresult',
            old_name='marm_implementing_organization_id',
            new_name='marm_implementing_organization',
        ),
        migrations.RenameField(
            model_name='closingresult',
            old_name='request_id',
            new_name='request',
        ),
        migrations.RenameField(
            model_name='refinement',
            old_name='closing_result_id',
            new_name='closing_result',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='address_id',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='defect_id',
            new_name='defect',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='implementing_organization_id',
            new_name='implementing_organization',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='user_id',
            new_name='user',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='closing_result_id',
            new_name='closing_result',
        ),
        migrations.RenameField(
            model_name='securityevents',
            old_name='work_performed_type_id',
            new_name='work_performed_type',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='implementing_organization_id',
            new_name='implementing_organization',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='organization_id',
            new_name='organization',
        ),
        migrations.AlterField(
            model_name='review',
            name='assessment_quality_work',
            field=models.PositiveSmallIntegerField(verbose_name='Оценка качества выполнения работ'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(('organization__isnull', False), ('implementing_organization__isnull', False), _connector='OR'), name='not_both_null'),
        ),
    ]
