# Generated by Django 3.2.5 on 2021-08-13 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0008_auto_20210813_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='Z7RCC9971U', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='token_str',
            field=models.CharField(default='FXITQLKVXJ', max_length=10),
        ),
    ]
