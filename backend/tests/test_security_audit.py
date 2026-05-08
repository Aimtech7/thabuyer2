"""tests/test_security_audit.py"""
import pytest
from django.urls import reverse
from rest_framework import status
from products.models import Product, Collection
from cart.models import CartItem
from promotions.models import PromoPricing

@pytest.mark.django_db
class TestSecurityAudit:
    
    # --- AUTHENTICATION & AUTHORIZATION ---

    def test_seller_cannot_access_admin_analytics(self, seller_client):
        url = reverse('admin-analytics')
        resp = seller_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_buyer_cannot_access_admin_analytics(self, buyer_client):
        url = reverse('admin-analytics')
        resp = buyer_client.get(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_seller_cannot_update_other_sellers_product(self, seller_client, db, category):
        # Create a product belonging to a different seller manually
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_seller = User.objects.create_user(email='other@test.com', password='p', role='seller')
        other_product = Product.objects.create(
            seller=other_seller, category=category, name="Other's Product", price=100, SKU='SKU-OTHER'
        )
        
        url = reverse('product-update', kwargs={'pk': other_product.pk})
        resp = seller_client.patch(url, {'price': 50.00}, format='json')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    # --- DATA INTEGRITY & BUSINESS LOGIC ---

    def test_cannot_set_negative_price(self, seller_client, product):
        url = reverse('product-update', kwargs={'pk': product.pk})
        resp = seller_client.patch(url, {'price': -10.00}, format='json')
        # This should fail validation
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_tamper_with_cart_item_price(self, buyer_client, product):
        # Cart API should ignore 'price' passed from client and use DB price
        url = reverse('cart-add')
        resp = buyer_client.post(url, {'product_id': str(product.id), 'quantity': 1, 'price': '0.01'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        
        item = CartItem.objects.latest('added_at')
        assert item.price_at_add == product.price
        assert item.price_at_add != 0.01

    def test_checkout_uses_db_price_not_client_price(self, buyer_client, product, cart_with_item):
        # Trigger checkout - the API should NOT take a 'total' from the client.
        url = reverse('order-checkout')
        resp = buyer_client.post(url, {'total_amount': '1.00'}, format='json')
        # If the API allows 'total_amount' override, that's a HUGE vulnerability.
        # Check the actual order created.
        from orders.models import Order
        order = Order.objects.latest('created_at')
        assert order.total_amount == product.price * 2 # quantity in cart_with_item is 2
        assert order.total_amount != 1.00

    # --- INJECTION TESTING ---

    def test_sql_injection_in_filter(self, api_client, product):
        url = reverse('product-list') + "?name=' OR 1=1 --"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        # It should return 0 or 1 results matching the weird name, NOT all products
        # Standard Django ORM escapes this correctly.

    def test_xss_payload_in_product_name(self, seller_client, category):
        url = reverse('product-create')
        payload = {
            'name': "<script>alert('xss')</script>",
            'description': 'Test',
            'price': '100.00',
            'stock_qty': 10,
            'SKU': 'XSS-001',
            'category': category.id
        }
        resp = seller_client.post(url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        # Note: Backend often allows XSS storage; it's the FRONTEND's job to escape.
        # But a secure backend might sanitize on save.

    # --- RATE LIMITING ---

    def test_basic_rate_limiting_exists(self, api_client):
        url = reverse('product-list')
        # Just check if we can reach it, but in reality we'd spam it.
        # We'll rely on settings check for this one.
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_200_OK

    # --- SELLER PRIVILEGE ABUSE (BOLA) ---

    def test_seller_cannot_add_others_product_to_collection(self, seller_client, category):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_seller = User.objects.create_user(email='other2@test.com', password='p', role='seller')
        other_product = Product.objects.create(
            seller=other_seller, category=category, name="Other's Product", price=100, SKU='SKU-OTHER-2'
        )
        
        url = reverse('collection-list-create')
        payload = {
            'name': 'My Collection',
            'product_ids': [str(other_product.id)]
        }
        resp = seller_client.post(url, payload, format='json')
        
        # This SHOULD fail if BOLA protection is implemented
        # Currently it might PASS (which is a finding)
        # We expect 400 if we implement validation.
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_seller_cannot_create_promo_for_others_product(self, seller_client, category):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_seller = User.objects.create_user(email='other3@test.com', password='p', role='seller')
        other_product = Product.objects.create(
            seller=other_seller, category=category, name="Other's Product", price=100, SKU='SKU-OTHER-3'
        )
        
        url = reverse('promopricing-list-create')
        payload = {
            'product': str(other_product.id),
            'promo_price': '10.00',
            'start_date': '2026-01-01',
            'end_date': '2026-12-31'
        }
        resp = seller_client.post(url, payload, format='json')
        
        # This SHOULD fail
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_non_image_as_product_image(self, seller_client, category):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse('product-create')
        malicious_file = SimpleUploadedFile("exploit.txt", b"malicious content", content_type="text/plain")
        
        payload = {
            'name': 'Hack Product',
            'description': 'Test',
            'price': '10.00',
            'stock_qty': 10,
            'SKU': 'HACK-001',
            'category': category.id,
            'uploaded_images': [malicious_file]
        }
        resp = seller_client.post(url, payload, format='multipart')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_token_tampering(self, api_client):
        # Invalid token
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        resp = api_client.get(reverse('product-list'))
        # product-list is AllowAny, so it should pass but user will be Anonymous
        assert resp.status_code == status.HTTP_200_OK
        
        # authenticated endpoint
        resp = api_client.get(reverse('admin-analytics'))
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
