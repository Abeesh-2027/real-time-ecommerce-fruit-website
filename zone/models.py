from django.db import models
from django.contrib.auth.models import User


class Fruit(models.Model):
    name       = models.CharField(max_length=100)
    price      = models.DecimalField(max_digits=8, decimal_places=2)
    image      = models.ImageField(upload_to='fruits/', blank=True, null=True)
    image_file = models.CharField(max_length=100, blank=True,
                                  help_text='Static filename e.g. apple.jpg')
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Fruits'

    def __str__(self):
        return f'{self.name} – ₹{self.price}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('pending',   'Pending'),
    ]
    PAYMENT_CHOICES = [
        ('upi',        'UPI'),
        ('card',       'Card'),
        ('netbanking', 'Net Banking'),
        ('cod',        'Cash on Delivery'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='zone_orders'
    )
    order_id            = models.CharField(max_length=20, unique=True)
    customer_name       = models.CharField(max_length=150)
    customer_phone      = models.CharField(max_length=15)
    customer_email      = models.EmailField()
    delivery_address    = models.TextField()
    delivery_notes      = models.TextField(blank=True)
    subtotal            = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge     = models.DecimalField(max_digits=6,  decimal_places=2, default=0)
    total               = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method      = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.order_id} – {self.customer_name} – ₹{self.total}'


class OrderItem(models.Model):
    order     = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    name      = models.CharField(max_length=100)
    price     = models.DecimalField(max_digits=8, decimal_places=2)
    quantity  = models.PositiveIntegerField(default=1)
    image_url = models.URLField(blank=True)

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.name} × {self.quantity}'