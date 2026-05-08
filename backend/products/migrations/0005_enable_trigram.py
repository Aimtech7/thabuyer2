from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0004_product_clicks_count_product_views_count_collection'),
    ]
    operations = [
        TrigramExtension(),
    ]
