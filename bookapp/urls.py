from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('verification/', views.verification, name='verification'),
    path('login/', views.login, name='login'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('test/', views.test, name='test'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('order-history/', views.order_history, name='order_history'),
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path('profile/listings/', views.profile_listings, name='profile_listings'),
    path('listing/', views.browse_listings, name='search'),
    path('listing/add/', views.add_listing, name='add_listing'),
    path('listing/remove/', views.remove_listing, name='remove_listing'),
    path('forgotPassword/', views.forgot, name='forgotPassword'),
    path('resetPassword/<str:extension>', views.resetpw, name='resetPassword'),
    path('bookinfo/<str:id>/', views.bookinfo, name='bookinfo'),
    path('cart/', views.cart, name='cart'),
    path('cart/checkout/<str:userid>', views.checkout, name='checkout'),
    path('payment/<str:userid>', views.payment, name='payment'),
]
