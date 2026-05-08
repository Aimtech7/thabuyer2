import pytest
from django.urls import reverse
from rest_framework import status
from orders.models import Order, OrderItem
from products.models import Product

@pytest.mark.django_db
class TestAnalytics:
    def test_seller_analytics(self, seller_client, seller_user, buyer):
        # Create a product and an order to generate analytics data
        product = Product.objects.create(
            seller=seller_user,
            name="Test Product",
            price=100.00,
            stock_qty=10
        )
        order = Order.objects.create(
            buyer=buyer,
            total_amount=100.00,
            status='delivered'
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            unit_price=100.00
        )

        url = reverse('analytics:seller-analytics')
        response = seller_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'monthly_revenue' in response.data['data']
        # Note: Depending on subtotal implementation, check value
        # In analytics/views.py it uses items__subtotal. 
        # Let's ensure OrderItem has subtotal or it might fail if not defined as a field.
    
    def test_export_orders_csv(self, admin_client, buyer):
        Order.objects.create(buyer=buyer, total_amount=50.00, status='pending')
        
        url = reverse('analytics:export-orders-csv')
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'orders_export.csv' in response['Content-Disposition']
        content = response.content.decode('utf-8')
        assert buyer.email in content
