import pytest
import uuid
from django.urls import reverse
from rest_framework import status
from products.models import Product, Category
from orders.models import Order
from cart.models import CartItem
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
class TestAPIStability:
    def test_product_list_query_efficiency(self, api_client, product):
        """
        Verify that the product list endpoint is efficient.
        """
        url = reverse('product-list')
        # We already have one product from fixture. Let's ensure it's loaded.
        with CaptureQueriesContext(connection) as queries:
            response = api_client.get(url)
        assert response.status_code == 200
        # For a single product, it should be very few queries.
        assert len(queries) < 15

    def test_api_rate_limiting_config(self, api_client):
        from rest_framework.settings import api_settings
        throttles = [t.__module__ + '.' + t.__name__ for t in api_settings.DEFAULT_THROTTLE_CLASSES]
        assert any('AnonRateThrottle' in t for t in throttles)
        assert any('UserRateThrottle' in t for t in throttles)

@pytest.mark.django_db
class TestDatabaseIntegrity:
    def test_checkout_atomicity_on_validation_failure(self, api_client, buyer, buyer_cart, product):
        api_client.force_authenticate(user=buyer)
        # Add item to cart
        CartItem.objects.create(cart=buyer_cart, product=product, quantity=5, price_at_add=product.price)
        
        url = reverse('order-checkout')
        # Empty data to trigger validation error (shipping_address is required)
        response = api_client.post(url, {})
        assert response.status_code == 400
        
        product.refresh_from_db()
        assert product.stock_qty == 50 # Original stock from fixture
        assert Order.objects.count() == 0

    def test_orphan_record_prevention(self, seller_user, product):
        product_id = product.id
        seller_user.delete()
        with pytest.raises(Product.DoesNotExist):
            Product.objects.get(id=product_id)

@pytest.mark.django_db
class TestSecurityHardening:
    def test_file_upload_type_restriction(self, api_client, seller_user, category):
        api_client.force_authenticate(user=seller_user)
        url = reverse('product-create')
        malicious_file = SimpleUploadedFile("exploit.sh", b"echo hacked", content_type="text/x-shellscript")
        data = {
            'name': 'Hacked Product',
            'price': 1.00,
            'stock_qty': 1,
            'SKU': 'HACK-001',
            'category': category.id,
            'uploaded_images': [malicious_file]
        }
        response = api_client.post(url, data, format='multipart')
        assert response.status_code == 400
        assert 'uploaded_images' in str(response.data)
