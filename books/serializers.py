from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookEnrichedSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    averageRating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'year', 'isbn', 'pages', 'stock', 'description', 'averageRating']

    @extend_schema_field(serializers.CharField())
    def get_description(self, obj):
        return getattr(obj, 'description', 'No description available')

    @extend_schema_field(serializers.FloatField())
    def get_averageRating(self, obj):
        return float(getattr(obj, 'averageRating', 0.0))