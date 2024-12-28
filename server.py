import django, os
import grpc
from concurrent import futures

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from books.models import Book
import book_pb2_grpc
import book_pb2


class BookService(book_pb2_grpc.BookServiceServicer):
    def GetBook(self, request, context):
        try:
            book = Book.objects.get(pk=request.book_id)
            print(book)
            return book_pb2.BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                year=book.year,
                isbn=book.isbn,
                pages=book.pages,
                stock=book.stock,
            )
        except Book.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Book not found')
            return book_pb2.BookResponse()

    def ListBooks(self, request, context):
        books = Book.objects.all()
        return book_pb2.BookList(
            books=[
                book_pb2.BookResponse(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    year=book.year,
                    isbn=book.isbn,
                    pages=book.pages,
                    stock=book.stock,
                )
                for book in books
            ]
        )

    def UpdateStock(self, request, context):
        try:
            book = Book.objects.get(pk=request.book_id)
            book.stock = request.stock
            book.save()
            return book_pb2.StockResponse(message="Stock updated successfully")
        except Book.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Book not found')
            return book_pb2.StockResponse(message="Book not found")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    book_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC server is running on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
