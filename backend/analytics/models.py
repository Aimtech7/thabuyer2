import uuid
from django.db import models

class DailyMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True, db_index=True)
    total_sales = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_sellers = models.PositiveIntegerField(default=0)
    top_selling_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'daily_metrics'
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}"
