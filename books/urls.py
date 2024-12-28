from django.urls import path

from .views import BookViewSet

urlpatterns = [
    path('books', BookViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('books/health', BookViewSet.as_view({
        'get': 'health_check',
    })),
    path('books/<str:pk>', BookViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }))
]