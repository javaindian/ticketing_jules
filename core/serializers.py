from rest_framework import serializers
from .models import User, Book, Transaction, Fee # Import all models that might need serialization

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__' # Includes all fields from the Book model
        read_only_fields = ['id', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    # Optionally, use nested serializers for better representation of related objects
    # user = UserSerializer(read_only=True) # Example of nested read-only user
    # book = BookSerializer(read_only=True) # Example of nested read-only book

    # Or use PrimaryKeyRelatedField for writable related fields
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'transaction_date'] # transaction_date is default=now

    def validate(self, data):
        """
        Custom validation for transactions.
        E.g., ensure a book is 'available' before checkout.
        Ensure user and book exist.
        """
        if data.get('transaction_type') == 'checkout':
            book = data.get('book')
            if book and book.status != 'available':
                raise serializers.ValidationError(f"Book '{book.title}' is not available for checkout. Current status: {book.status}.")
            if not data.get('due_date'):
                 # Set default due_date if not provided, or handled by model's save method
                pass # Model save method handles this
        return data

class FeeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), allow_null=True, required=False)
    transaction = serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Fee
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# More specific serializers can be created later, e.g., for checkout/return operations.
class BookSearchSerializer(serializers.ModelSerializer): # For book search results
    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'isbn', 'category', 'status']

class TransactionCreateSerializer(serializers.ModelSerializer): # For creating transactions
    class Meta:
        model = Transaction
        fields = ['user', 'book', 'transaction_type', 'due_date'] # return_date is not for creation

    def create(self, validated_data):
        # Custom logic on creation, e.g. updating book status
        transaction = super().create(validated_data)
        if transaction.transaction_type == 'checkout':
            transaction.book.status = 'borrowed'
            transaction.book.save(update_fields=['status'])
        # Add logic for 'return' if this serializer is also used for returns,
        # or use a different serializer for returns.
        return transaction

class TransactionReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        # Assuming we identify the transaction to return by its ID in the URL
        # and only update its return_date and potentially create a Fee.
        fields = ['return_date'] # Could add notes or other return-specific fields
        # `transaction_date` should be `timezone.now` by default in model or view

    def update(self, instance, validated_data):
        instance.return_date = validated_data.get('return_date', timezone.now())
        instance.transaction_type = 'return' # Ensure type is set to return
        instance.book.status = 'available'
        instance.book.save(update_fields=['status'])

        # Basic overdue fee calculation
        # This should be more robust, potentially in a service or model method
        if instance.due_date and instance.return_date.date() > instance.due_date:
            overdue_days = (instance.return_date.date() - instance.due_date).days
            fee_amount = overdue_days * 0.50 # $0.50 per day
            if fee_amount > 0:
                Fee.objects.create(
                    user=instance.user,
                    book=instance.book,
                    transaction=instance,
                    fee_type='overdue',
                    amount=fee_amount,
                    notes=f"Overdue by {overdue_days} day(s)."
                )
        return super().update(instance, validated_data)
