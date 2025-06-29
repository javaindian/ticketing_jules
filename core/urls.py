from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BookViewSet, TransactionViewSet, FeeViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'books', BookViewSet, basename='book')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'fees', FeeViewSet, basename='fee')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
