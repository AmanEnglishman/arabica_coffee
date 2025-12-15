from django.urls import path
from apps.cart.api.views.cart import CartView, AddCartItemView, UpdateCartItemView, DeleteCartItemView

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart-view"),
    path("cart/item/", AddCartItemView.as_view(), name="add-cart-item"),
    path("cart/item/<int:pk>/", UpdateCartItemView.as_view(), name="update-cart-item"),
    path("cart/item/<int:pk>/", DeleteCartItemView.as_view(), name="delete-cart-item"),
]