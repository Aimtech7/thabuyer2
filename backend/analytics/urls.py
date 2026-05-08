from django.urls import path
from .views import SellerAnalyticsView, ExportOrderCSVView, SellerReportPDFView

app_name = 'analytics'

urlpatterns = [
    path('seller/stats/', SellerAnalyticsView.as_view(), name='seller-analytics'),
    path('admin/export/orders/', ExportOrderCSVView.as_view(), name='export-orders-csv'),
    path('seller/report/pdf/', SellerReportPDFView.as_view(), name='seller-report-pdf'),
]
