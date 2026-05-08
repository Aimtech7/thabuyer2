"""tests/test_wishlists.py — Wishlist model & API tests."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestWishlistModel:
    def test_wishlist_created_on_add(self, buyer_client, product):
        url = reverse('wishlist-add')
        resp = buyer_client.post(url, {'product_id': str(product.id)}, format='json')
        assert resp.status_code == 201
        assert resp.data['status'] == 'success'

    def test_wishlist_view_returns_items(self, buyer_client, product):
        buyer_client.post(reverse('wishlist-add'), {'product_id': str(product.id)}, format='json')
        resp = buyer_client.get(reverse('wishlist'))
        assert resp.status_code == 200
        assert resp.data['data']['item_count'] == 1

    def test_add_same_product_is_idempotent(self, buyer_client, product):
        url = reverse('wishlist-add')
        buyer_client.post(url, {'product_id': str(product.id)}, format='json')
        resp = buyer_client.post(url, {'product_id': str(product.id)}, format='json')
        # Second add returns 200, not 201
        assert resp.status_code == 200
        assert resp.data['message'] == 'Already in wishlist.'

    def test_remove_product_from_wishlist(self, buyer_client, product):
        buyer_client.post(reverse('wishlist-add'), {'product_id': str(product.id)}, format='json')
        resp = buyer_client.delete(reverse('wishlist-remove'), {'product_id': str(product.id)}, format='json')
        assert resp.status_code == 200
        # Verify item count is now 0
        get_resp = buyer_client.get(reverse('wishlist'))
        assert get_resp.data['data']['item_count'] == 0

    def test_remove_nonexistent_item_returns_404(self, buyer_client, product):
        resp = buyer_client.delete(reverse('wishlist-remove'), {'product_id': str(product.id)}, format='json')
        assert resp.status_code == 404

    def test_clear_wishlist(self, buyer_client, product):
        buyer_client.post(reverse('wishlist-add'), {'product_id': str(product.id)}, format='json')
        resp = buyer_client.delete(reverse('wishlist-clear'))
        assert resp.status_code == 200
        get_resp = buyer_client.get(reverse('wishlist'))
        assert get_resp.data['data']['item_count'] == 0

    def test_wishlist_requires_buyer_auth(self, seller_client):
        resp = seller_client.get(reverse('wishlist'))
        assert resp.status_code == 403

    def test_wishlist_requires_login(self, api_client):
        resp = api_client.get(reverse('wishlist'))
        assert resp.status_code == 401
