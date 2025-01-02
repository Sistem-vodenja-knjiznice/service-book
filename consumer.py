import django, pika, os
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

load_dotenv()

from books.models import Book
from books.etcd_gateway import get_etcd_key

MESSAGE_BROKER_URL = get_etcd_key('MESSAGE_BROKER_URL')

params = pika.URLParameters(MESSAGE_BROKER_URL)

connection = pika.BlockingConnection(params)

channel = connection.channel()
channel.queue_declare(queue='borrow')


def callback(ch, method, properties, body):
    if properties.content_type == 'book_borrowed':
        book = Book.objects.get(id=body)
        book.stock -= 1
        book.save()

    elif properties.content_type == 'book_returned':
        book = Book.objects.get(id=body)
        book.stock += 1
        book.save()


channel.basic_consume(queue='borrow', on_message_callback=callback, auto_ack=True)

print('Started Consuming')

channel.start_consuming()

channel.close()