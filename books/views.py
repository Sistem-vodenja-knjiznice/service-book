from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Book
from .serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all books",
        description="Returns a list of all books.",
        responses=BookSerializer,
    ),
    retrieve=extend_schema(
        summary="Get a book by ID",
        description="Returns a single book by its ID.",
        responses=BookSerializer,
    ),
    create=extend_schema(
        summary="Create a book",
        description="Creates a new book.",
        request=BookSerializer,
        responses=BookSerializer,
    ),
    update=extend_schema(
        summary="Update a book",
        description="Updates an existing book.",
        request=BookSerializer,
        responses=BookSerializer,
    ),
    destroy=extend_schema(
        summary="Delete a book",
        description="Deletes a book.",
    ),
)
class BookViewSet(viewsets.ViewSet):
    def list(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        book = Book.objects.get(id=pk)
        serializer = BookSerializer(book)

        return Response(serializer.data)


    def create(self, request):
        serializer = BookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        book = Book.objects.get(id=pk)
        serializer = BookSerializer(instance=book, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        book = Book.objects.get(id=pk)
        book.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def health_check(request):
        health_status = {"status": "healthy"}
        return JsonResponse(health_status, status=200)