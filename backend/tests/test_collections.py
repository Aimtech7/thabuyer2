"""tests/test_collections.py — Product Collection model & API tests."""
import pytest
from django.urls import reverse
from products.models import Collection


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_collection(seller_user, name='Summer Sale', slug='summer-sale'):
    return Collection.objects.create(
        seller=seller_user,
        name=name,
        slug=slug,
        is_active=True,
    )


# ─── Model Tests ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCollectionModel:
    def test_collection_creation(self, seller_user, seller_profile):
        col = make_collection(seller_user)
        assert col.name == 'Summer Sale'
        assert col.is_active is True
        assert col.seller == seller_user

    def test_str_representation(self, seller_user, seller_profile):
        col = make_collection(seller_user)
        assert 'Summer Sale' in str(col)

    def test_products_many_to_many(self, seller_user, seller_profile, product):
        col = make_collection(seller_user)
        col.products.add(product)
        assert col.products.count() == 1
        assert product in col.products.all()

    def test_unique_together_seller_slug(self, seller_user, seller_profile):
        make_collection(seller_user)
        with pytest.raises(Exception):
            make_collection(seller_user, name='Duplicate Slug', slug='summer-sale')

    def test_two_sellers_can_share_slug(self, seller_user, seller_profile, db):
        """Different sellers can use the same slug."""
        from django.contrib.auth import get_user_model
        from sellers.models import SellerProfile
        User = get_user_model()
        seller2 = User.objects.create_user(
            email='seller2@test.com', password='TestPass123!',
            name='Seller Two', role='seller', verified=True,
        )
        SellerProfile.objects.create(user=seller2, business_name='Store Two')
        col1 = make_collection(seller_user)
        col2 = Collection.objects.create(seller=seller2, name='Summer Sale', slug='summer-sale')
        assert col1.slug == col2.slug  # allowed, different seller


# ─── API Tests ────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCollectionListCreateAPI:
    def test_seller_can_list_collections(self, seller_client, seller_user, seller_profile):
        make_collection(seller_user)
        make_collection(seller_user, name='Winter Drop', slug='winter-drop')
        resp = seller_client.get(reverse('collection-list-create'))
        assert resp.status_code == 200
        assert resp.data['count'] == 2
        assert len(resp.data['results']) == 2

    def test_seller_sees_only_own_collections(self, seller_client, seller_user, seller_profile, db):
        """Collections from a different seller must NOT appear in the list."""
        from django.contrib.auth import get_user_model
        from sellers.models import SellerProfile
        User = get_user_model()
        seller2 = User.objects.create_user(
            email='seller2@test.com', password='TestPass123!',
            name='Seller Two', role='seller', verified=True,
        )
        SellerProfile.objects.create(user=seller2, business_name='Store Two')
        make_collection(seller_user, name='My Collection', slug='my-col')
        Collection.objects.create(seller=seller2, name='Other Collection', slug='other-col')
        resp = seller_client.get(reverse('collection-list-create'))
        assert resp.status_code == 200
        results = resp.data['results']
        names = [c['name'] for c in results]
        assert 'My Collection' in names
        assert 'Other Collection' not in names

    def test_seller_can_create_collection(self, seller_client, seller_profile):
        payload = {'name': 'Flash Sale'}
        resp = seller_client.post(reverse('collection-list-create'), payload, format='json')
        print(f"DEBUG RESPONSE: {resp.data}")
        assert resp.status_code == 201
        assert resp.data['name'] == 'Flash Sale'
        assert resp.data['slug'] == 'flash-sale'

    def test_buyer_cannot_create_collection(self, buyer_client):
        payload = {'name': 'Flash Sale'}
        resp = buyer_client.post(reverse('collection-list-create'), payload, format='json')
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access(self, api_client):
        resp = api_client.get(reverse('collection-list-create'))
        assert resp.status_code == 401


@pytest.mark.django_db
class TestCollectionDetailAPI:
    def test_seller_can_retrieve_own_collection(self, seller_client, seller_user, seller_profile):
        col = make_collection(seller_user)
        url = reverse('collection-detail', kwargs={'pk': col.id})
        resp = seller_client.get(url)
        assert resp.status_code == 200
        assert resp.data['name'] == 'Summer Sale'

    def test_seller_can_update_collection(self, seller_client, seller_user, seller_profile):
        col = make_collection(seller_user)
        url = reverse('collection-detail', kwargs={'pk': col.id})
        resp = seller_client.patch(url, {'name': 'Mega Sale'}, format='json')
        assert resp.status_code == 200
        col.refresh_from_db()
        assert col.name == 'Mega Sale'

    def test_seller_can_delete_collection(self, seller_client, seller_user, seller_profile):
        col = make_collection(seller_user)
        url = reverse('collection-detail', kwargs={'pk': col.id})
        resp = seller_client.delete(url)
        assert resp.status_code == 204
        assert not Collection.objects.filter(pk=col.id).exists()

    def test_seller_cannot_access_other_sellers_collection(self, seller_client, seller_profile, db):
        """Seller must receive 404 for a collection they do not own."""
        from django.contrib.auth import get_user_model
        from sellers.models import SellerProfile
        User = get_user_model()
        seller2 = User.objects.create_user(
            email='seller2@test.com', password='TestPass123!',
            name='Seller Two', role='seller', verified=True,
        )
        SellerProfile.objects.create(user=seller2, business_name='Store Two')
        col = Collection.objects.create(seller=seller2, name='Other Col', slug='other-col')
        url = reverse('collection-detail', kwargs={'pk': col.id})
        resp = seller_client.get(url)
        assert resp.status_code == 404

    def test_retrieve_nonexistent_collection_returns_404(self, seller_client, seller_profile):
        import uuid
        url = reverse('collection-detail', kwargs={'pk': uuid.uuid4()})
        resp = seller_client.get(url)
        assert resp.status_code == 404


# ─── Analytics — View & Click Tracking ───────────────────────────────────────

@pytest.mark.django_db
class TestProductAnalytics:
    def test_product_detail_increments_views_count(self, api_client, product):
        initial_views = product.views_count
        url = reverse('product-detail', kwargs={'pk': product.id})
        api_client.get(url)
        product.refresh_from_db()
        assert product.views_count == initial_views + 1

    def test_product_click_increments_clicks_count(self, api_client, product):
        initial_clicks = product.clicks_count
        url = reverse('product-click', kwargs={'pk': product.id})
        api_client.post(url)
        product.refresh_from_db()
        assert product.clicks_count == initial_clicks + 1

    def test_click_on_nonexistent_product_returns_404(self, api_client):
        import uuid
        url = reverse('product-click', kwargs={'pk': uuid.uuid4()})
        resp = api_client.post(url)
        assert resp.status_code == 404

    def test_multiple_views_accumulate(self, api_client, product):
        url = reverse('product-detail', kwargs={'pk': product.id})
        for _ in range(3):
            api_client.get(url)
        product.refresh_from_db()
        assert product.views_count >= 3

    def test_dashboard_exposes_analytics_totals(self, seller_client, seller_user, seller_profile, product):
        """SellerDashboard should return total_views & total_clicks."""
        resp = seller_client.get(reverse('seller-dashboard'))
        assert resp.status_code == 200
        data = resp.data['data']
        assert 'total_views' in data
        assert 'total_clicks' in data
