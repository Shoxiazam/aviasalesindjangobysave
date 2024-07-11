from django.conf import settings 
from django.conf.urls.static import static
from django.urls import path
from . import views



urlpatterns = [
    path('', views.search_flights, name='search'),
    path('hotels/', views.search_hotels, name='hotels'),
    path('hotel/<int:pk>/', views.hotel_detail, name='hotel_detail'),
    path('city/', views.city_list, name='city_list'),
    path('city/<int:city_id>/', views.city_detail, name='city_detail'),
    path('search/', views.search_apartments, name='search_apartments'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('login/',views.login_page,name='login'),
    path('logout/',views.logout_page,name='logout'),
    path('singup/',views.signup_page,name='signup'),
    path('profile/', views.profile, name='profile'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('booking/create/', views.booking_create, name='booking_create'),
    path('buy-ticket/<int:booking_id>/', views.buy_ticket, name='buy_ticket'),
    path('purchase_history/', views.purchase_history, name='purchase_history'),
    path('create_profile/', views.create_profile, name='create_profile'),
    path('random-ad/', views.random_advertisement, name='random_advertisement'),
    path('booking_success/<str:cashback_amount>/', views.booking_success, name='booking_success'),
    path('buy_subscription/', views.buy_subscription, name='buy_subscription'),
    path('edit/<int:booking_id>/', views.booking_edit, name='booking_edit'),
    path('cancel/<int:booking_id>/', views.booking_cancel, name='booking_cancel'),
    path('subscribe/select/', views.subscribe_select, name='subscribe_select'),
    path('subscribe/purchase/', views.purchase_info, name='purchase_info'),
      
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  
