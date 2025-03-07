from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample
import requests

from .models import Book
from .serializers import BookSerializer, BookEnrichedSerializer
from .etcd_gateway import get_etcd_key

@extend_schema_view(
    list=extend_schema(
        summary="List all books",
        description="Returns a list of all books in the database.",
        responses={
            200: OpenApiResponse(
                response=BookSerializer(many=True),
                description="List of books",
            ),
            400: OpenApiResponse(
                description="Bad Request"
            ),
        },
    ),
    retrieve=extend_schema(
        summary="Get a book by ID",
        description="Returns a single book by its ID.",
        responses={
            200: OpenApiResponse(
                response=BookEnrichedSerializer,
                description="Book details",
            ),
            404: OpenApiResponse(
                description="Book not found",
            ),
        },
    ),
    create=extend_schema(
        summary="Create a book",
        description="Creates a new book.",
        request=BookSerializer,
        responses={
            201: OpenApiResponse(
                response=BookSerializer,
                description="Created book",
            ),
            400: OpenApiResponse(
                description="Validation error",
            ),
        },
    ),
    update=extend_schema(
        summary="Update a book",
        description="Updates an existing book.",
        request=BookSerializer,
        responses={
            202: OpenApiResponse(
                response=BookSerializer,
                description="Updated book",
            ),
            400: OpenApiResponse(
                description="Validation error",
            ),
            404: OpenApiResponse(
                description="Book not found",
            ),
        },
    ),
    destroy=extend_schema(
        summary="Delete a book",
        description="Deletes a book.",
        responses={
            204: OpenApiResponse(
                description="Book deleted successfully",
            ),
            404: OpenApiResponse(
                description="Book not found",
            ),
        },
    ),
    health_check=extend_schema(
        summary="Health check",
        description="Returns the health status of the service.",
        responses={
            200: OpenApiResponse(
                description="Service is healthy",
                examples=[
                    OpenApiExample(
                        name="Health Check Response",
                        value={"status": "healthy"},
                        response_only=True,
                    )
                ],
            ),
        },
    ),
)
class BookViewSet(viewsets.ViewSet):
    def list(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        book = Book.objects.get(id=pk)

        GOOGLE_API_KEY = get_etcd_key('GOOGLE_API_KEY')
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in etcd")

        google_books_api_url = f"https://www.googleapis.com/books/v1/volumes?q={book.title}&key={GOOGLE_API_KEY}&langRestrict=en"

        response = requests.get(google_books_api_url)
        if response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch data from Google Books API'},
                                status=response.status_code)

        serializer = BookSerializer(book)
        serialized_data = serializer.data

        try:
            serialized_data['description'] = response.json()['items'][0]['volumeInfo']['description']
        except:
            serialized_data['description'] = 'No description available'

        try:
            serialized_data['averageRating'] = response.json()['items'][0]['volumeInfo']['averageRating']
        except:
            serialized_data['averageRating'] = 'No rating available'

        return Response(serialized_data)

    @csrf_exempt
    def create(self, request):
        serializer = BookSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        DO_SERVERLESS_API = get_etcd_key('DO_SERVERLESS_API')
        serverless_url = f'{DO_SERVERLESS_API}/book/add'

        response = requests.post(serverless_url, json={
            'title': serializer.data['title'],
            'author': serializer.data['author'],
            'year': serializer.data['year'],
            'pages': serializer.data['pages'],
            'isbn': serializer.data['isbn'],
            'stock': serializer.data['stock']
        })

        if response.status_code == 200:
            book_data = response.json()
            new_book = Book(
                title=book_data['title'],
                author=book_data['author'],
                year=book_data['year'],
                pages=book_data['pages'],
                isbn=book_data['isbn'],
                stock=book_data['stock'],
            )
            new_book.save()

            new_serializer = BookSerializer(data=new_book)

            return Response(new_serializer.data, status=status.HTTP_201_CREATED)

        else:
            return JsonResponse({'error': response.json()['body']}, status=response.status_code)

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

    @action(detail=False, methods=['get'], url_path='health')
    def health_check(self, request):
        health_status = {"status": "healthy"}
        return JsonResponse(health_status, status=200)