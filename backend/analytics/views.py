import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count
from django.utils import timezone
from io import BytesIO
from reportlab.pdfgen import canvas
from orders.models import Order
from .models import DailyMetric
from core.permissions import IsSeller

class SellerAnalyticsView(APIView):
    """
    Detailed sales analytics for the current seller.
    """
    permission_classes = [IsSeller]

    def get(self, request):
        user = request.user
        # Monthly revenue
        revenue = Order.objects.filter(
            items__product__seller=user,
            status__in=['processing', 'shipped', 'delivered']
        ).aggregate(total=Sum('items__subtotal'))['total'] or 0

        # Top products
        top_products = Order.objects.filter(
            items__product__seller=user
        ).values('items__product__name').annotate(
            total_sold=Sum('items__quantity')
        ).order_by('-total_sold')[:5]

        return Response({
            'status': 'success',
            'data': {
                'monthly_revenue': str(revenue),
                'top_products': top_products
            }
        })

class ExportOrderCSVView(APIView):
    """
    Export all orders to CSV (Admin only).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Buyer', 'Total', 'Status', 'Created At'])

        orders = Order.objects.all().select_related('buyer')
        for order in orders:
            writer.writerow([order.id, order.buyer.email, order.total_amount, order.status, order.created_at])

        return response


class SellerReportPDFView(APIView):
    """
    Generate a PDF performance report for the current seller.
    """
    permission_classes = [IsSeller]

    def get(self, request):
        user = request.user
        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, f"Seller Performance Report: {user.email}")

        p.setFont("Helvetica", 12)
        p.drawString(100, 780, f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Fetch some data
        revenue = Order.objects.filter(
            items__product__seller=user,
            status__in=['processing', 'shipped', 'delivered']
        ).aggregate(total=Sum('items__subtotal'))['total'] or 0

        p.drawString(100, 750, f"Total Revenue: ${float(revenue):.2f}")

        # Top Products
        p.drawString(100, 730, "Top 5 Products by Quantity Sold:")
        top_products = Order.objects.filter(
            items__product__seller=user
        ).values('items__product__name').annotate(
            total_sold=Sum('items__quantity')
        ).order_by('-total_sold')[:5]

        y = 710
        for prod in top_products:
            p.drawString(120, y, f"- {prod['items__product__name']}: {prod['total_sold']} units")
            y -= 20

        p.showPage()
        p.save()

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="seller_report_{user.id}.pdf"'
        return response
