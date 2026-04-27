from django.urls import path
from . import views

app_name = 'zone'

urlpatterns = [
    # Auth
    path('',        views.login_view,  name='login'),
    path('login/',  views.login_view,  name='login_alt'),
    path('logout/', views.logout_view, name='logout'),

    # Pages
    path('home/',     views.home_view,     name='home'),
    path('products/', views.products_view, name='product'),
    path('cart/',     views.cart_view,     name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('success/',  views.success_view,  name='success'),
    path('orders/',   views.orders_view,   name='orders'),
    path('view/',     views.view_order_view, name='view'),   # FIX: dedicated view, not orders_view

    # Contact
    path('contact/', views.contact_view, name='contact'),

    # Razorpay API
    path('api/razorpay/create-order/', views.razorpay_create_order, name='razorpay_create'),
    path('api/razorpay/verify/',       views.razorpay_verify,        name='razorpay_verify'),

    # Order API
    path('api/orders/', views.api_place_order, name='api_orders'),
]