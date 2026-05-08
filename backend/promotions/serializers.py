from rest_framework import serializers
from .models import Coupon, PromoPricing
from products.serializers import ProductSerializer

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('seller',)

    def create(self, validated_data):
        seller = self.context['request'].user
        return Coupon.objects.create(seller=seller, **validated_data)

class PromoPricingSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = PromoPricing
        fields = ('id', 'product', 'product_details', 'promotional_price', 'start_date', 'end_date', 'is_active')
        read_only_fields = ('id',)

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("End date must be after start date.")
        return data
