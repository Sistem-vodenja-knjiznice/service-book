from rest_framework import viewsets, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, extend_schema_view
import requests, os, etcd3

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

        etcd = etcd3.client(host=os.getenv('ETCD_HOST'),
                            port=os.getenv('ETCD_PORT'),
                            user=os.getenv('ETCD_USERNAME'),
                            password=os.getenv('ETCD_PASSWORD'))

        GOOGLE_API_KEY = etcd.get('GOOGLE_API_KEY')[0]
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

        DO_SERVERLESS_API = os.getenv('DO_SERVERLESS_API')
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

    def health_check(self, request):
        health_status = {"status": "healthy"}
        return JsonResponse(health_status, status=200)