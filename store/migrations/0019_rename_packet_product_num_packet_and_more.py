# Generated by Django 5.1.1 on 2024-10-31 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_remove_cartitem_cart_remove_sale_cart_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='packet',
            new_name='num_packet',
        ),
        migrations.RemoveField(
            model_name='product',
            name='quantity',
        ),
        migrations.AddField(
            model_name='product',
            name='packet_contain',
            field=models.PositiveBigIntegerField(default=24),
            preserve_default=False,
        ),
    ]
