from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import User, Book, Transaction, Fee
from .serializers import (
    UserSerializer, BookSerializer, TransactionSerializer, FeeSerializer,
    BookSearchSerializer, TransactionCreateSerializer, TransactionReturnSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # Or more granular permissions

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for books. Supports viewing, creating, editing, deleting,
    and searching books by title or author.
    """
    queryset = Book.objects.all().order_by('title')
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow read for anyone, write for authenticated
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'language', 'publisher']
    search_fields = ['title', 'authors', 'isbn', 'category'] # Fields for /api/books/?search=...
    ordering_fields = ['title', 'published_date', 'created_at']

    # The plan asks for search by title/author specifically.
    # The `search_fields` above already enable this via ?search=
    # If a dedicated endpoint /api/books/search is desired:
    @action(detail=False, methods=['get'], serializer_class=BookSearchSerializer, url_path='search')
    def search_books(self, request):
        """
        Custom search action for books.
        Example: /api/books/search/?title=Test&author=AuthorName
        """
        title_query = request.query_params.get('title', None)
        author_query = request.query_params.get('author', None)

        queryset = self.get_queryset() # Start with the base queryset

        if title_query:
            queryset = queryset.filter(title__icontains=title_query)
        if author_query:
            queryset = queryset.filter(authors__icontains=author_query)

        # Could add more filters here like category, isbn etc.

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing transactions.
    Includes custom actions for checkout and return.
    """
    queryset = Transaction.objects.all().order_by('-transaction_date')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser] # Typically only librarians/admins manage transactions
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'book', 'transaction_type', 'due_date', 'return_date']
    ordering_fields = ['transaction_date', 'due_date']

    def get_serializer_class(self):
        if self.action == 'checkout':
            return TransactionCreateSerializer
        if self.action == 'process_return': # Changed from 'return_book' to avoid conflict with HTTP method name
            return TransactionReturnSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        Creates a checkout transaction.
        Expects: user_id, book_id in request data.
        Due date can be optionally provided, otherwise defaults (e.g. in model or serializer).
        """
        serializer = TransactionCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            book = serializer.validated_data['book']
            if book.status != 'available':
                return Response({'error': f"Book '{book.title}' is not available. Status: {book.status}."},
                                status=status.HTTP_400_BAD_REQUEST)

            transaction = serializer.save(transaction_type='checkout')
            # Book status is updated in TransactionCreateSerializer's create method
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Using PUT on a specific transaction ID for return seems more RESTful
    # e.g. PUT /api/transactions/{id}/return/
    # This action is on a specific transaction instance
    @action(detail=True, methods=['post'], url_path='return') # Changed to POST for action, detail=True
    def process_return(self, request, pk=None):
        """
        Processes a book return for a given transaction ID.
        Updates the transaction's return_date and the book's status.
        Calculates overdue fees if applicable.
        """
        try:
            transaction = self.get_object()
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found.'}, status=status.HTTP_404_NOT_FOUND)

        if transaction.transaction_type != 'checkout' or transaction.return_date is not None:
             return Response({'error': 'This transaction is not a valid checkout or has already been returned.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Use TransactionReturnSerializer for the update
        # Pass data like {'return_date': 'YYYY-MM-DDTHH:MM:SSZ'} or let it default to now
        serializer = TransactionReturnSerializer(transaction, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save() # The serializer's update method handles book status and fee creation
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing fees.
    Usually fees are created automatically, but this allows viewing and manual adjustment/payment marking.
    """
    queryset = Fee.objects.all().order_by('-created_at')
    serializer_class = FeeSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins manage fees directly
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'book', 'paid_status', 'fee_type']
    ordering_fields = ['amount', 'created_at', 'payment_date']

    @action(detail=True, methods=['post'], url_path='mark-as-paid')
    def mark_as_paid(self, request, pk=None):
        fee = self.get_object()
        if fee.paid_status:
            return Response({'message': 'Fee is already marked as paid.'}, status=status.HTTP_400_BAD_REQUEST)
        fee.paid_status = True
        fee.payment_date = timezone.now()
        fee.save(update_fields=['paid_status', 'payment_date'])
        return Response(FeeSerializer(fee).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-as-unpaid')
    def mark_as_unpaid(self, request, pk=None):
        fee = self.get_object()
        if not fee.paid_status:
            return Response({'message': 'Fee is already marked as unpaid.'}, status=status.HTTP_400_BAD_REQUEST)
        fee.paid_status = False
        fee.payment_date = None
        fee.save(update_fields=['paid_status', 'payment_date'])
        return Response(FeeSerializer(fee).data, status=status.HTTP_200_OK)
