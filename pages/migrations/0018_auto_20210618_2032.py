# Generated by Django 3.2.4 on 2021-06-18 18:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0017_remove_orderline_ordered'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productquantity',
            old_name='point_id',
            new_name='point',
        ),
        migrations.RenameField(
            model_name='productquantity',
            old_name='product_id',
            new_name='product',
        ),
    ]
