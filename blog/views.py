from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
import random
import logging
from .models import Profile, Flight, Hotel, City, Apartment, Booking, UserSubscription, PurchaseHistory, Advertisement, Subscription
from .forms import ProfileForm, BookingForm, SearchForm, SubscriptionForm, SubscriptionSelectForm, PaymentForm

logger = logging.getLogger(__name__)

def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return HttpResponse("Your password and confirm password are not the same!!")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            return redirect('login')

    return render(request, 'signup.html')       

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                return redirect('create_profile')
            return redirect('profile')
        else:
            return HttpResponse("Username or Password is incorrect!!!")
    return render(request, 'login.html')

@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    try:
        profile = Profile.objects.get(user=user)
        bookings = Booking.objects.filter(user=user)
    except Profile.DoesNotExist:
        messages.warning(request, 'Profile does not exist. Please create a profile.')
        return redirect('create_profile')
    return render(request, 'profile.html', {'user': user, 'profile': profile, 'bookings': bookings})



@login_required
def search_flights(request):
    user_subscription = getattr(request.user, 'usersubscription', None)
    
    flights = Flight.objects.all()

    if request.method == 'POST':
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        payment = request.POST.get('payment')
        passenger_type = request.POST.get('passenger_type')

        if origin:
            flights = flights.filter(origin__icontains=origin)
        if destination:
            flights = flights.filter(destination__icontains=destination)
        if departure_date:
            flights = flights.filter(departure_date=departure_date)
        if return_date:
            flights = flights.filter(return_date=return_date)
        if payment and payment != 'Любая':
            flights = flights.filter(payment=payment)
        if passenger_type and passenger_type != 'классы':
            flights = flights.filter(passenger_type=passenger_type)

    flight_data = []
    for flight in flights:
        price = flight.discounted_price(user_subscription)
        discount_percentage = user_subscription.subscription.discount_percentage if user_subscription and user_subscription.subscription else 0.0
        flight_data.append({
            'flight': flight,
            'price': price,
            'discount_percentage': discount_percentage
        })

    return render(request, 'index.html', {'results': flight_data, 'user_subscription': user_subscription})








def search_hotels(request):
    query = request.GET.get('query')
    checkin_date = request.GET.get('checkin_date')
    checkout_date = request.GET.get('checkout_date')
    guests = request.GET.get('guests')

    hotels = Hotel.objects.all()
    if query:
        hotels = hotels.filter(name__icontains=query)

    return render(request, 'hotel.html', {'hotels': hotels})

def hotel_detail(request, pk):
    hotel = Hotel.objects.get(pk=pk)
    return render(request, 'hotel.html', {'hotel': hotel})

def city_list(request):
    cities = City.objects.all()
    return render(request, 'uyo_buyo.html', {'cities': cities})

def city_detail(request, city_id):
    city = get_object_or_404(City, id=city_id)
    return render(request, 'uyo_buyo_list.html', {'city': city})

def search_apartments(request):
    form = SearchForm(request.GET or None)
    apartments = Apartment.objects.all()

    if form.is_valid():
        city = form.cleaned_data.get('city')
        date_checkin = form.cleaned_data.get('date_checkin')
        date_checkout = form.cleaned_data.get('date_checkout')
        guests = form.cleaned_data.get('guests')

        if city:
            apartments = apartments.filter(city__icontains=city)

    return render(request, 'apartments.html', {'form': form, 'apartments': apartments})







@login_required
def booking_create(request):
    initial_data = {}
    
    # Получаем параметры из GET запроса
    flight_id = request.GET.get('flight_id')
    hotel_id = request.GET.get('hotel_id')
    apartment_id = request.GET.get('apartment_id')
    
    if flight_id:
        try:
            initial_data['flight'] = Flight.objects.get(id=flight_id)
        except Flight.DoesNotExist:
            pass

    if hotel_id:
        try:
            initial_data['hotel'] = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            pass

    if apartment_id:
        try:
            initial_data['apartment'] = Apartment.objects.get(id=apartment_id)
        except Apartment.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BookingForm(request.POST, initial=initial_data, user=request.user)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.calculate_cashback()
                booking.calculate_final_price()
                booking.save()
                logger.info(f"Booking created with ID: {booking.id}")
                return redirect('buy_ticket', booking_id=booking.id)
            except Exception as e:
                logger.error(f"Error saving booking: {e}")
                return HttpResponse("Error saving booking", status=500)
        else:
            logger.warning("Form is not valid")
    else:
        form = BookingForm(initial=initial_data, user=request.user)
    
    return render(request, 'booking_form.html', {'form': form})




@login_required
def buy_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()

            # Добавляем бронирование в профиль пользователя
            profile = Profile.objects.get(user=request.user)
            profile.bookings.add(booking)

            # Перенаправление на страницу подтверждения бронирования
            return redirect('profile')
    else:
        form = BookingForm(instance=booking)

    context = {
        'form': form,
        'booking': booking,
        'final_price': booking.final_price,
        'cashback_amount': booking.cashback_amount
    }
    return render(request, 'buy_ticket.html', context)




@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'buy_ticket.html', {'booking': booking})









@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'booking_list.html', {'bookings': bookings})




@login_required
def purchase_history(request):
    history = PurchaseHistory.objects.filter(user=request.user)
    return render(request, 'profile.html', {'history': history})

def get_price(self, user):
    try:
        subscription = user.usersubscription
        discount = subscription.discount
        discounted_price = self.price * (1 - discount / 100)
        return discounted_price
    except UserSubscription.DoesNotExist:
        return self.price

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('profile')
    else:
        form = ProfileForm()
    return render(request, 'profile_form.html', {'form': form})

def random_advertisement(request):
    advertisements = Advertisement.objects.all()
    random_ad = random.choice(advertisements) if advertisements.exists() else None
    
    if random_ad:
        html = f"""
        <div class="advertisement">
            <h2>{random_ad.title}</h2>
            <img src="{random_ad.image.url}" alt="{random_ad.title}">
            <p>{random_ad.description}</p>
        </div>
        """
    else:
        html = "<p>No advertisements available at the moment.</p>"
    
    return HttpResponse(html)

@login_required
def booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'booking_edit.html', {'form': form})

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST':
        booking.delete()
        return redirect('profile')
    return render(request, 'booking_cancel.html', {'booking': booking})

@login_required
def restricted_view(request):
    if request.user.usersubscription.has_subscription:
        return render(request, 'index.html')
    else:
        return redirect('subscribe')
    




@login_required
def subscribe(request):
    user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SubscriptionForm(request.POST, user=request.user, instance=user_subscription)
        if form.is_valid():
            form.save()
            return redirect('buy_subscription')
    else:
        form = SubscriptionForm(user=request.user, instance=user_subscription)

    return render(request, 'subscribe.html', {'form': form, 'subscription': user_subscription})

@login_required
def buy_subscription(request):
    user_subscription = get_object_or_404(UserSubscription, user=request.user)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            user_subscription.purchases_count += 1
            user_subscription.update_discount()
            user_subscription.save()
            return redirect('profile')
    else:
        form = PaymentForm()

    return render(request, 'buy_subscription.html', {'form': form, 'subscription': user_subscription.subscription})



def subscribe_select(request):
    form = SubscriptionSelectForm(request.POST or None)
    if form.is_valid():
        subscription = form.cleaned_data['subscription']
        request.session['selected_subscription'] = subscription.id
        return redirect('purchase_info')

    return render(request, 'subscribe_select.html', {'form': form})

def purchase_info(request):
    if 'selected_subscription' not in request.session:
        return redirect('subscribe_select')

    subscription_id = request.session['selected_subscription']
    subscription = get_object_or_404(Subscription, id=subscription_id)

    if request.method == 'POST':
        profile = request.user.profile
        profile.subscription = subscription
        profile.save()
        del request.session['selected_subscription']
        return redirect('profile')

    return render(request, 'purchase_info.html', {'subscription': subscription})


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
