# Generated by Django 3.2.5 on 2021-08-18 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0013_auto_20210818_1936'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='R6YO8WPS3W', max_length=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='picture',
            field=models.ImageField(blank=True, default='images/no_image.png', null=True, upload_to='images', verbose_name='picture'),
        ),
        migrations.AlterField(
            model_name='expense',
            name='token_str',
            field=models.CharField(default='BCDWCBWM6X', max_length=10),
        ),
    ]
