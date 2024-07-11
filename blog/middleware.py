from django.shortcuts import redirect, reverse
from django.contrib.auth import get_user_model
from .models import UserSubscription

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                subscription = UserSubscription.objects.get(user=request.user)
            except UserSubscription.DoesNotExist:
                # Просто продолжаем выполнение запроса, если нет подписки
                pass

        response = self.get_response(request)
        return response
