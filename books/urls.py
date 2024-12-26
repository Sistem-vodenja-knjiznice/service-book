from django.urls import path

from .views import BookViewSet

urlpatterns = [
    path('books', BookViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('books/<str:pk>', BookViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }))
]