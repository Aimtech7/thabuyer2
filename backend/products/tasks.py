from celery import shared_task
from django.db.models import F
from .models import Product

@shared_task
def increment_product_views(product_id):
    """Asynchronously increment product views count to reduce request-time DB pressure."""
    Product.objects.filter(pk=product_id).update(views_count=F('views_count') + 1)

@shared_task
def increment_product_clicks(product_id):
    """Asynchronously increment product clicks count."""
    Product.objects.filter(pk=product_id).update(clicks_count=F('clicks_count') + 1)
