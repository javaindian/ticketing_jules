import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'), # For library admins, not superuser
    )
    # Add an id field for consistency with other models if needed, though AbstractUser has one.
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')

    def __str__(self):
        return self.username

class Book(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost'),
        ('reserved', 'Reserved'), # Added reserved status
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(max_length=13, unique=True, help_text='13 Character ISBN')
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=500) # Simplified for now
    category = models.CharField(max_length=100, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.isbn})"

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('checkout', 'Checkout'),
        ('return', 'Return'),
        ('renew', 'Renew'), # Added renew type
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactions') # Protect user from deletion if they have transactions
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='transactions') # Protect book from deletion if it has transactions
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateTimeField(default=timezone.now) # Renamed from checkout_date for clarity
    due_date = models.DateField(null=True, blank=True) # Nullable for return transactions
    return_date = models.DateTimeField(null=True, blank=True)
    # notes = models.TextField(blank=True, null=True) # Optional notes for the transaction

    def __str__(self):
        return f"{self.transaction_type} - {self.book.title} by {self.user.username} on {self.transaction_date.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if self.transaction_type == 'checkout' and not self.due_date:
            # Example: Set due date to 2 weeks from now
            self.due_date = timezone.now().date() + timezone.timedelta(weeks=2)
        super().save(*args, **kwargs)


class Fee(models.Model):
    FEE_TYPE_CHOICES = (
        ('overdue', 'Overdue'),
        ('lost_book', 'Lost Book'),
        ('damage', 'Damage'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Link to User directly instead of Transaction for more flexibility
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fees')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='fees') # In case book is deleted
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='fee_record') # Use OneToOneField if a fee is uniquely tied to one transaction causing it.
                                                                                                                            # Or ForeignKey if multiple fees can arise from one transaction (e.g. overdue + damage)
    fee_type = models.CharField(max_length=10, choices=FEE_TYPE_CHOICES, default='overdue')
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    paid_status = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fee for {self.user.username} - ${self.amount} ({'Paid' if self.paid_status else 'Unpaid'})"

# Consider OtherMedia for later as per refined plan
# class OtherMedia(models.Model):
#     MEDIA_TYPE_CHOICES = (
#         ('journal', 'Journal'),
#         ('ebook', 'eBook'),
#         ('magazine', 'Magazine'),
#     )
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     title = models.CharField(max_length=255)
#     media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
#     authors = models.CharField(max_length=500, blank=True) # Authors might not apply to all media
#     publisher = models.CharField(max_length=255, blank=True)
#     published_date = models.DateField(null=True, blank=True)
#     category = models.CharField(max_length=100, blank=True)
#     status = models.CharField(max_length=10, choices=Book.STATUS_CHOICES, default='available') # Reusing Book's status choices
#     location_url = models.URLField(max_length=500, blank=True, null=True) # For ebooks or online journals
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.title} ({self.media_type})"
