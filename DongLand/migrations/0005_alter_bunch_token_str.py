# Generated by Django 3.2.5 on 2021-08-06 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DongLand', '0004_bunch_token_str'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bunch',
            name='token_str',
            field=models.CharField(default='N66K68Z97H', max_length=10),
        ),
    ]
