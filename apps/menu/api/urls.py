from django.urls import path
from .views import ProductDetailAPIView, ProductSearchAPIView, MenuAPIView, BulkImportView

urlpatterns = [
    path('', MenuAPIView.as_view(), name='menu'),
    path('<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('bulk-import/', BulkImportView.as_view(), name='bulk-import'),
]
