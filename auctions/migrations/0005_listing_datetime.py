# Generated by Django 4.2.2 on 2023-06-21 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_listing_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='dateTime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
