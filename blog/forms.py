from .models import Profile
from django import forms
from .models import Booking,Subscription,UserSubscription




class FlightSearchForm(forms.Form):
    origin = forms.CharField(label='Откуда', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Откуда'}))
    destination = forms.CharField(label='Куда', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Куда'}))
    departure_date = forms.DateField(label='Когда', widget=forms.TextInput(attrs={'type': 'date', 'placeholder': 'Когда'}))
    return_date = forms.DateField(label='Обратно', required=False, widget=forms.TextInput(attrs={'type': 'date', 'placeholder': 'Обратно'}))



class SearchForm(forms.Form):
    city = forms.CharField(max_length=100, required=False)
    date_checkin = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    date_checkout = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    guests = forms.IntegerField(min_value=1, required=False)
    


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['flight', 'hotel', 'apartment', 'booking_type', 'guest_name', 'check_in', 'check_out', 'guests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['guest_name'].initial = user.username

        self.fields['flight'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['hotel'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['apartment'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['booking_type'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['guest_name'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['check_in'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['check_out'].widget.attrs.update({'class': 'form-control mb-2'})
        self.fields['guests'].widget.attrs.update({'class': 'form-control mb-2'})

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'avatar', 'bio', 'phone_number']


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = UserSubscription
        fields = ['subscription']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['subscription'].queryset = Subscription.objects.all()

class PaymentForm(forms.Form):
    card_number = forms.CharField(max_length=16, label="Card Number")
    card_expiry = forms.CharField(max_length=5, label="Card Expiry (MM/YY)")
    card_cvv = forms.CharField(max_length=3, label="CVV")






class SubscriptionSelectForm(forms.Form):
    subscription = forms.ModelChoiceField(queryset=Subscription.objects.all(), empty_label=None, widget=forms.RadioSelect)
    
    
    
class BookingPaymentForm(forms.ModelForm):
    card_number = forms.CharField(label='Card Number', max_length=16, widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Enter your card number'}))
    card_expiry = forms.CharField(label='Card Expiry', max_length=5, widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'MM/YY'}))
    card_cvv = forms.CharField(label='CVV', max_length=4, widget=forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'CVV'}))

    class Meta:
        model = Booking
        fields = [
            'flight', 'hotel', 'apartment', 'booking_type', 
            'guest_name', 'check_in', 'check_out', 'guests'
        ]
        widgets = {
            'flight': forms.Select(attrs={'class': 'form-select mt-1 block w-full'}),
            'hotel': forms.Select(attrs={'class': 'form-select mt-1 block w-full'}),
            'apartment': forms.Select(attrs={'class': 'form-select mt-1 block w-full'}),
            'booking_type': forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Booking type'}),
            'guest_name': forms.TextInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Guest name'}),
            'check_in': forms.DateInput(attrs={'class': 'form-input mt-1 block w-full', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-input mt-1 block w-full', 'type': 'date'}),
            'guests': forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full', 'placeholder': 'Number of guests'}),
        }