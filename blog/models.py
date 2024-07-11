from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='city_images/')
    
    

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    bookings = models.ManyToManyField('Booking', blank=True)

    def __str__(self):
        return self.user.username
    
# models.py

class Flight(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    def discounted_price(self, user_subscription=None):
        print(f"Base price: {self.base_price}")
        if user_subscription and user_subscription.subscription:
            discount_percentage = user_subscription.subscription.discount_percentage
            discounted_price = self.base_price * (1 - discount_percentage / 100)
            print(f"Discounted Price: {discounted_price} with Discount Percentage: {discount_percentage}")
            return discounted_price
        else:
            return self.base_price 

    def __str__(self):
        return f"{self.origin} to {self.destination} ({self.departure_date})"


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    def discounted_price(self, user_subscription=None):
        # Calculate discounted price based on user subscription
        if user_subscription and user_subscription.subscription:
            discount_percentage = user_subscription.subscription.discount_percentage
            discounted_price = self.price * (1 - discount_percentage / 100)
            return discounted_price
        else:
            return self.price

    def __str__(self):
        return self.name

class Apartment(models.Model):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    country = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='apartments/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def discounted_price(self, user_subscription=None):
        # Calculate discounted price based on user subscription
        if user_subscription and user_subscription.subscription:
            discount_percentage = user_subscription.subscription.discount_percentage
            discounted_price = self.price_per_night * (1 - discount_percentage / 100)
            return discounted_price
        else:
            return self.price_per_night

    def __str__(self):
        return self.name




class Subscription(models.Model):
    name = models.CharField(max_length=100)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    purchases_count = models.IntegerField(default=50)
    
    def update_discount(self):
        if self.purchases_count >= 10:
            self.discount_percentage = 70.0
        elif self.purchases_count >= 5:
            self.discount_percentage = 25.0
        else:
            self.discount_percentage = 0.0
        self.save()

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    purchases_count = models.IntegerField(default=50)

    def update_purchases_count(self):
        if self.subscription:
            self.purchases_count = self.subscription.purchases_count
            self.save()

    def update_discount(self):
        if self.subscription:
            if self.purchases_count >= 10:
                self.subscription.discount_percentage = 70.0
            elif self.purchases_count >= 5:
                self.subscription.discount_percentage = 25.0
            else:
                self.subscription.discount_percentage = 0.0
            self.subscription.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.start_date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.subscription:
            return f"{self.user.username} - Subscription: {self.subscription.name} - Purchases Count: {self.purchases_count}"
        else:
            return f"{self.user.username} - No Subscription - Purchases Count: {self.purchases_count}"



   
from datetime import date, timedelta
from decimal import Decimal

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey('Flight', on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, null=True, blank=True)
    apartment = models.ForeignKey('Apartment', on_delete=models.CASCADE, null=True, blank=True)
    booking_type = models.CharField(max_length=100)
    guest_name = models.CharField(max_length=255)
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.IntegerField()
    cashback_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'), editable=False)

    def calculate_cashback(self):
        cashback = Decimal('0.0')
        booking_duration = (self.check_out - self.check_in).days

        if self.hotel or self.apartment:
            cashback += Decimal('0.05')

        if booking_duration > 7:
            cashback += Decimal('0.03')

        if self.flight:
            cashback += Decimal('0.02')

        self.cashback_amount = self.total_cost * cashback
        return self.cashback_amount

    def calculate_final_price(self):
        self.final_price = self.total_cost - self.cashback_amount
        return self.final_price

    def save(self, *args, **kwargs):
        self.calculate_cashback()
        self.calculate_final_price()
        super().save(*args, **kwargs)




class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.flight}'
    

class Advertisement(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='ads/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
    

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Purchase by {self.user.username} for booking ID {self.booking.id}'
    
    
# views.py



def get_booking_info(request):
    booking_type = request.GET.get('type')
    booking_id = request.GET.get('id')

    if booking_type == 'flight':
        flight = get_object_or_404(Flight, pk=booking_id)
        user_info = f'Имя пользователя: {request.user.profile.user.username}' if request.user.profile else 'Пользователь не указал имя'
        return JsonResponse({'booking_info': f'{flight.origin} в {flight.destination} на {flight.departure_date} за ${flight.discounted_price:.2f} (со скидкой {flight.discount_percentage}%)', 'user_info': user_info, 'guest_name': request.user.profile.user.username})
    elif booking_type == 'hotel':
        hotel = get_object_or_404(Hotel, pk=booking_id)
        user_info = f'Имя пользователя: {request.user.profile.user.username}' if request.user.profile else 'Пользователь не указал имя'
        return JsonResponse({'booking_info': f'Информация о гостинице: {hotel.name}, Адрес: {hotel.address}, Цена: ${hotel.discounted_price:.2f}', 'user_info': user_info, 'guest_name': request.user.profile.user.username})
    elif booking_type == 'apartment':
        apartment = get_object_or_404(Apartment, pk=booking_id)
        user_info = f'Имя пользователя: {request.user.profile.user.username}' if request.user.profile else 'Пользователь не указал имя'
        return JsonResponse({'booking_info': f'Информация об апартаментах: {apartment.name}, Адрес: {apartment.address}, Цена: ${apartment.discounted_price:.2f}', 'user_info': user_info, 'guest_name': request.user.profile.user.username})
    else:
        return JsonResponse({'error': 'Invalid booking type'}, status=400)
