# Generated by Django 3.2.5 on 2021-08-23 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0018_auto_20210819_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='XPGB4ZKO55', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='token_str',
            field=models.CharField(default='IK1JOFFEN5', max_length=10),
        ),
    ]
