"""tests/test_promotions.py — Coupon & PromoPricing model & API tests."""
import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from promotions.models import Coupon, PromoPricing


# ─── Helpers ──────────────────────────────────────────────────────────────────

def make_coupon(seller_profile, code='SAVE10', discount_type='fixed', amount=Decimal('10.00')):
    return Coupon.objects.create(
        code=code,
        discount_type=discount_type,
        discount_amount=amount,
        active=True,
        seller_restricted=seller_profile,
    )


def make_promo(product, offset_hours=1):
    now = timezone.now()
    return PromoPricing.objects.create(
        product=product,
        promo_price=Decimal('149.99'),
        start_date=now - timedelta(hours=offset_hours),
        end_date=now + timedelta(hours=24),
        is_active=True,
    )


# ─── Coupon Model Tests ────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCouponModel:
    def test_coupon_creation(self, seller_profile):
        coupon = make_coupon(seller_profile)
        assert coupon.code == 'SAVE10'
        assert coupon.active is True
        assert coupon.discount_type == 'fixed'

    def test_str_representation(self, seller_profile):
        coupon = make_coupon(seller_profile)
        assert 'SAVE10' in str(coupon)
        assert 'fixed' in str(coupon)

    def test_code_is_unique(self, seller_profile):
        make_coupon(seller_profile)
        with pytest.raises(Exception):
            make_coupon(seller_profile, code='SAVE10')  # duplicate code

    def test_coupon_is_valid_when_active(self, seller_profile):
        coupon = make_coupon(seller_profile)
        assert coupon.is_valid() is True

    def test_inactive_coupon_is_not_valid(self, seller_profile):
        coupon = make_coupon(seller_profile)
        coupon.active = False
        coupon.save()
        assert coupon.is_valid() is False

    def test_coupon_invalid_when_usage_limit_reached(self, seller_profile):
        coupon = Coupon.objects.create(
            code='LIMITED',
            discount_type='fixed',
            discount_amount=Decimal('5.00'),
            active=True,
            seller_restricted=seller_profile,
            usage_limit=3,
            times_used=3,
        )
        assert coupon.is_valid() is False

    def test_coupon_invalid_when_expired(self, seller_profile):
        past = timezone.now() - timedelta(days=1)
        coupon = Coupon.objects.create(
            code='EXPIRED',
            discount_type='fixed',
            discount_amount=Decimal('5.00'),
            active=True,
            seller_restricted=seller_profile,
            valid_until=past,
        )
        assert coupon.is_valid() is False

    def test_coupon_invalid_when_not_yet_started(self, seller_profile):
        future = timezone.now() + timedelta(days=1)
        coupon = Coupon.objects.create(
            code='FUTURE',
            discount_type='fixed',
            discount_amount=Decimal('5.00'),
            active=True,
            seller_restricted=seller_profile,
            valid_from=future,
        )
        assert coupon.is_valid() is False

    def test_percent_discount_type(self, seller_profile):
        coupon = Coupon.objects.create(
            code='PCT20',
            discount_type='percent',
            discount_amount=Decimal('20.00'),
            active=True,
        )
        assert coupon.discount_type == 'percent'


# ─── Coupon API Tests ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCouponAPI:
    def test_seller_can_list_coupons(self, seller_client, seller_profile):
        make_coupon(seller_profile, code='FIRST')
        make_coupon(seller_profile, code='SECOND')
        resp = seller_client.get(reverse('coupon-list-create'))
        assert resp.status_code == 200
        assert resp.data['count'] == 2
        assert len(resp.data['results']) == 2

    def test_buyer_cannot_access_coupons(self, buyer_client):
        resp = buyer_client.get(reverse('coupon-list-create'))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access_coupons(self, api_client):
        resp = api_client.get(reverse('coupon-list-create'))
        assert resp.status_code == 401


# ─── PromoPricing Model Tests ──────────────────────────────────────────────────

@pytest.mark.django_db
class TestPromoPricingModel:
    def test_promo_creation(self, product):
        promo = make_promo(product)
        assert promo.promo_price == Decimal('149.99')
        assert promo.is_active is True

    def test_str_representation(self, product):
        promo = make_promo(product)
        assert product.name in str(promo)

    def test_is_currently_active_for_valid_promo(self, product):
        promo = make_promo(product)
        assert promo.is_currently_active is True

    def test_is_currently_active_false_when_deactivated(self, product):
        promo = make_promo(product)
        promo.is_active = False
        promo.save()
        assert promo.is_currently_active is False

    def test_is_currently_active_false_when_future(self, product):
        now = timezone.now()
        promo = PromoPricing.objects.create(
            product=product,
            promo_price=Decimal('99.99'),
            start_date=now + timedelta(hours=1),
            end_date=now + timedelta(hours=25),
            is_active=True,
        )
        assert promo.is_currently_active is False

    def test_is_currently_active_false_when_expired(self, product):
        now = timezone.now()
        promo = PromoPricing.objects.create(
            product=product,
            promo_price=Decimal('99.99'),
            start_date=now - timedelta(hours=48),
            end_date=now - timedelta(hours=1),
            is_active=True,
        )
        assert promo.is_currently_active is False

    def test_one_promo_per_product(self, product):
        """PromoPricing is OneToOne with Product — second create must fail."""
        make_promo(product)
        with pytest.raises(Exception):
            PromoPricing.objects.create(
                product=product,
                promo_price=Decimal('89.99'),
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=1),
            )


# ─── PromoPricing API Tests ────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPromoPricingAPI:
    def test_seller_can_list_promos(self, seller_client, seller_profile, product):
        make_promo(product)
        resp = seller_client.get(reverse('promopricing-list-create'))
        assert resp.status_code == 200
        assert resp.data['count'] == 1
        assert len(resp.data['results']) == 1

    def test_buyer_cannot_access_promos(self, buyer_client):
        resp = buyer_client.get(reverse('promopricing-list-create'))
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access_promos(self, api_client):
        resp = api_client.get(reverse('promopricing-list-create'))
        assert resp.status_code == 401

    def test_seller_can_retrieve_own_promo(self, seller_client, seller_profile, product):
        promo = make_promo(product)
        url = reverse('promopricing-detail', kwargs={'pk': promo.id})
        resp = seller_client.get(url)
        assert resp.status_code == 200

    def test_seller_can_delete_promo(self, seller_client, seller_profile, product):
        promo = make_promo(product)
        url = reverse('promopricing-detail', kwargs={'pk': promo.id})
        resp = seller_client.delete(url)
        assert resp.status_code == 204
        assert not PromoPricing.objects.filter(pk=promo.id).exists()
