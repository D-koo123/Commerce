# Generated by Django 5.1.1 on 2024-10-18 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_alter_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='user_bid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
