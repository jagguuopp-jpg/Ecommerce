import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User 

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=250, unique=True)
    category_slug = models.SlugField(max_length=100, unique=True, blank=True)
    category_created_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def save(self, *args, **kwargs):
        if not self.category_slug:
            self.category_slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    PART_TYPE_CHOICES = (
        ('cpu', 'Processor (CPU)'),
        ('gpu', 'Graphics Card (GPU)'),
        ('motherboard', 'Motherboard'),
        ('ram', 'RAM (Memory)'),
        ('storage', 'Storage (SSD/HDD)'),
        ('psu', 'Power Supply (PSU)'),
        ('cabinet', 'Cabinet / Case'),
        ('cooler', 'CPU Cooler'),
        ('other', 'Other Component'),
    )

    product_name = models.CharField(max_length=250, unique=True)
    product_slug = models.SlugField(max_length=100, unique=True, blank=True)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to='products/', blank=True, null=True)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    part_type = models.CharField(max_length=30, choices=PART_TYPE_CHOICES, blank=True, null=True, verbose_name="PC Part Type")
    product_created_at = models.DateField(auto_now_add=True)
    product_quantity_in_stock = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def save(self, *args, **kwargs):
        if not self.product_slug:
            self.product_slug = slugify(self.product_name)
        if not self.part_type:
            self.part_type = self.detect_part_type()
        super().save(*args, **kwargs)

    def detect_part_type(self):
        name = self.product_name.lower()
        if 'ryzen' in name or 'core i' in name or 'processor' in name or 'cpu' in name:
            return 'cpu'
        if 'rtx' in name or 'gtx' in name or 'geforce' in name or 'radeon' in name or 'gpu' in name:
            return 'gpu'
        if 'motherboard' in name or 'b650' in name or 'z790' in name or 'b760' in name:
            return 'motherboard'
        if 'ram' in name or 'ddr4' in name or 'ddr5' in name or 'vengeance' in name or 'trident' in name:
            return 'ram'
        if 'ssd' in name or 'nvme' in name or 'hdd' in name or 'storage' in name:
            return 'storage'
        if 'psu' in name or 'power supply' in name or '850w' in name or '750w' in name or '1000w' in name:
            return 'psu'
        if 'case' in name or 'cabinet' in name or 'chassis' in name or 'o11' in name or '4000d' in name or 'h9' in name:
            return 'cabinet'
        if 'cooler' in name or 'aio' in name or 'liquid' in name or 'ak620' in name or 'kraken' in name:
            return 'cooler'
        return 'other'

    def __str__(self):
        return self.product_name


class Whishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='Product')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


Wishlist = Whishlist


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    session_key = models.CharField(max_length=50, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        username = self.user.username if self.user else "Guest"
        return f"{username} -> {self.product.product_name} ({self.quantity})"

    def get_subtotal(self):
        return self.product.product_price * self.quantity


# Indian States and Major Cities Dictionary
INDIAN_STATES_AND_CITIES = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Tirupati", "Kurnool", "Kakinada", "Rajahmundry", "Other"],
    "Arunachal Pradesh": ["Itanagar", "Tawang", "Naharlagun", "Pasighat", "Ziro", "Other"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tinsukia", "Tezpur", "Other"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga", "Bihar Sharif", "Other"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon", "Other"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda", "Other"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar", "Anand", "Other"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Karnal", "Hisar", "Rohtak", "Panchkula", "Other"],
    "Himachal Pradesh": ["Shimla", "Dharamshala", "Solan", "Mandi", "Kullu", "Manali", "Baddi", "Other"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar", "Hazaribagh", "Other"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi", "Davanagere", "Ballari", "Kalaburagi", "Other"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Palakkad", "Alappuzha", "Kannur", "Other"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Dewas", "Satna", "Other"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Chhatrapati Sambhajinagar", "Solapur", "Navi Mumbai", "Other"],
    "Manipur": ["Imphal", "Churachandpur", "Thoubal", "Kakching", "Other"],
    "Meghalaya": ["Shillong", "Tura", "Jowai", "Nongpoh", "Other"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai", "Serchhip", "Other"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang", "Other"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri", "Balasore", "Other"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot", "Other"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara", "Alwar", "Other"],
    "Sikkim": ["Gangtok", "Namchi", "Geyzing", "Mangan", "Other"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tiruppur", "Erode", "Vellore", "Other"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam", "Other"],
    "Tripura": ["Agartala", "Dharmanagar", "Udaipur", "Kailashahar", "Other"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Noida", "Greater Noida", "Ghaziabad", "Varanasi", "Agra", "Prayagraj", "Meerut", "Bareilly", "Aligarh", "Other"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rishikesh", "Nainital", "Other"],
    "West Bengal": ["Kolkata", "Howrah", "Siliguri", "Durgapur", "Asansol", "Bardhaman", "Kharagpur", "Other"],
    "Andaman and Nicobar Islands": ["Port Blair", "Other"],
    "Chandigarh": ["Chandigarh", "Other"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Diu", "Silvassa", "Other"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi", "Central Delhi", "Other"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Udhampur", "Other"],
    "Ladakh": ["Leh", "Kargil", "Other"],
    "Lakshadweep": ["Kavaratti", "Other"],
    "Puducherry": ["Puducherry", "Karaikal", "Mahe", "Yanam", "Other"]
}

STATE_CHOICES = [(s, s) for s in INDIAN_STATES_AND_CITIES.keys()]


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address_line1 = models.CharField(max_length=255)  # House / Flat / Building
    address_line2 = models.CharField(max_length=255, blank=True, null=True)  # Street / Area / Landmark
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, choices=STATE_CHOICES, default='Delhi')
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='India')
    address_type = models.CharField(max_length=20, default='home')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'address'
        verbose_name_plural = 'addresses'

    def __str__(self):
        name = self.full_name or self.user.username
        return f"{name} - {self.address_line1}, {self.city}, {self.state} ({self.postal_code})"


class Order(models.Model):
    STATUS_CHOICES = (
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Exchange Requested', 'Exchange Requested'),
    )

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Order ID (UUID)")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address_text = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='UPI')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Confirmed')
    cancellation_reason = models.TextField(blank=True, null=True)
    exchange_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Razorpay Order ID")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Razorpay Payment ID")
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True, verbose_name="Razorpay Signature")

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_id} - {self.user.username} (₹{self.total_amount})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def get_subtotal(self):
        return self.price * self.quantity



class Enquiry(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    )

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'enquiry'
        verbose_name_plural = 'enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.status})"


# Aliases for backwards compatibility
Categories = Category
categories = Category
Products = Product
products = Product
Orders = Order
orders = Order
Enquiries = Enquiry
enquiries = Enquiry
