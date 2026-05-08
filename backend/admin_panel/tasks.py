"""admin_panel/tasks.py — Celery tasks for admin reporting."""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='admin_panel.tasks.generate_daily_report')
def generate_daily_report():
    """
    Generates a daily platform summary and logs it.
    In production, extend this to email admins or push to a dashboard.
    """
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    from orders.models import Order
    from django.db.models import Sum

    User = get_user_model()
    yesterday = timezone.now() - timedelta(days=1)

    new_users = User.objects.filter(date_joined__gte=yesterday).count()
    new_orders = Order.objects.filter(created_at__gte=yesterday).count()
    revenue = Order.objects.filter(
        created_at__gte=yesterday,
        status__in=['processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    report = {
        'date': yesterday.strftime('%Y-%m-%d'),
        'new_users': new_users,
        'new_orders': new_orders,
        'revenue': float(revenue),
    }
    logger.info('Daily Report: %s', report)
    return report


@shared_task(name='admin_panel.tasks.check_system_health')
def check_system_health():
    """Checks the health of various components (DB, Redis, etc.)"""
    from django.db import connections
    from django.utils import timezone
    import redis
    from django.conf import settings

    status = {'db': 'ok', 'redis': 'ok', 'timestamp': str(timezone.now())}

    # DB Check
    try:
        db_conn = connections['default']
        with db_conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        status['db'] = f'error: {str(e)}'

    # Redis Check (via Celery Broker URL)
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
    except Exception as e:
        status['redis'] = f'error: {str(e)}'

    logger.info('System Health Check: %s', status)
    return status
