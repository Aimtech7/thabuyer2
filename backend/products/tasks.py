from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from notifications.models import Notification

@shared_task
def check_price_freshness():
    """
    Scans for products that haven't been updated in 30 days.
    Creates an in-app notification for the respective sellers.
    """
    threshold_date = timezone.now() - timedelta(days=30)
    
    # Find active products updated more than 30 days ago
    stale_products = Product.objects.filter(
        is_active=True,
        updated_at__lt=threshold_date
    ).select_related('seller')

    notifications_to_create = []
    
    for product in stale_products:
        notifications_to_create.append(
            Notification(
                recipient=product.seller,
                title="Stale Price Alert",
                message=f"Your product '{product.name}' hasn't been updated in 30 days. Please review its price to ensure it remains competitive.",
                notification_type="price_alert",
                related_entity_id=str(product.id),
                related_entity_type="product"
            )
        )
    
    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        
    return f"Created {len(notifications_to_create)} price freshness notifications."
