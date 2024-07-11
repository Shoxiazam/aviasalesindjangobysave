from django.contrib import admin
from .models import Subscription,Advertisement,Purchase,Flight, Hotel,  City ,Booking, Apartment, Profile, Apartment, UserSubscription

admin.site.register(City)

admin.site.register(Flight)

admin.site.register(Hotel)



admin.site.register(Booking)


admin.site.register(Profile)

admin.site.register(Apartment)

admin.site.register(Purchase)
admin.site.register(UserSubscription)
admin.site.register(Subscription)
admin.site.register(Advertisement)