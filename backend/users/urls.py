from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('users/subscriptions', SubscriptionViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
]
