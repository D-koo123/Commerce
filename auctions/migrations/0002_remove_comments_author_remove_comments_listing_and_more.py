# Generated by Django 5.1.1 on 2024-10-15 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='author',
        ),
        migrations.RemoveField(
            model_name='comments',
            name='listing',
        ),
        migrations.RemoveField(
            model_name='listing',
            name='user',
        ),
        migrations.RemoveField(
            model_name='watchlist',
            name='listing',
        ),
        migrations.RemoveField(
            model_name='watchlist',
            name='author',
        ),
        migrations.DeleteModel(
            name='Bids_table',
        ),
        migrations.DeleteModel(
            name='Comments',
        ),
        migrations.DeleteModel(
            name='Listing',
        ),
        migrations.DeleteModel(
            name='Watchlist',
        ),
    ]
