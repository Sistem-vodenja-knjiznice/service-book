from django.urls import path

from .views import UserViewSet

urlpatterns = [
    path('books', UserViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('books/<str:pk>', UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }))
]