import json
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Q
from store.models import Category, Product, Whishlist, CartItem, Address, INDIAN_STATES_AND_CITIES, Order, OrderItem, Enquiry
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import razorpay
from django.conf import settings
import json
from django.http import JsonResponse
from store.AI import get_ai_parts


def get_builder_parts():
    return {
        'cpus': Product.objects.filter(part_type='cpu'),
        'motherboards': Product.objects.filter(part_type='motherboard'),
        'gpus': Product.objects.filter(part_type='gpu'),
        'rams': Product.objects.filter(part_type='ram'),
        'storages': Product.objects.filter(part_type='storage'),
        'psus': Product.objects.filter(part_type='psu'),
        'cabinets': Product.objects.filter(part_type='cabinet'),
        'coolers': Product.objects.filter(part_type='cooler'),
    }


def home(request):
    try:
        category_param = request.GET.get('category')
        selected_category_obj = None

        if category_param:
            if category_param == 'custom-pc-build-parts':
                products = Product.objects.filter(part_type__in=['cpu', 'gpu', 'motherboard', 'ram', 'storage', 'psu', 'cabinet', 'cooler'])
                selected_category_obj = Category.objects.filter(category_slug='custom-pc-build-parts').first()
            elif category_param.isdigit():
                products = Product.objects.filter(product_category_id=int(category_param))
                selected_category_obj = Category.objects.filter(id=int(category_param)).first()
            else:
                products = Product.objects.filter(product_category__category_slug=category_param)
                selected_category_obj = Category.objects.filter(category_slug=category_param).first()
        else:
            products = Product.objects.all()

        wishlist_ids = []
        if request.user.is_authenticated:
            wishlist_ids = list(Whishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        
        return render(request, 'home.html', {
            'products': products,
            'wishlist_ids': wishlist_ids,
            'selected_category': category_param,
            'selected_category_obj': selected_category_obj
        })
    except Exception as e:
        print("Error in home view:", e)
        return render(request, 'home.html', {'products': [], 'wishlist_ids': []})


def categories_view(request):
    try:
        categories = Category.objects.all()
        return render(request, 'categories.html', {
            'categories': categories
        })
    except Exception as e:
        print("Error in categories_view:", e)
        return redirect('home')


def get_product_detail(request, pslug=None):
    try:
        product = None
        slug = pslug or request.GET.get('slug')
        if slug:
            product = Product.objects.filter(product_slug=slug).first()
        
        if not product:
            pid = request.GET.get('id')
            if pid:
                product = Product.objects.filter(id=pid).first()
        
        if not product:
            product = Product.objects.first()

        is_in_wishlist = False
        if request.user.is_authenticated and product:
            is_in_wishlist = Whishlist.objects.filter(user=request.user, product=product).exists()

        payload = {
            'product': product,
            'is_in_wishlist': is_in_wishlist
        }
        return render(request, "product_detail.html", payload)
    except Exception as e:
        print("Error in product detail view:", e)
        return redirect('home')


def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')

            if not username or not password:
                messages.error(request, 'Please enter both username and password.')
                return redirect('login')

            if '@' in username:
                user_obj = User.objects.filter(email__iexact=username).first()
            else:
                user_obj = User.objects.filter(username__iexact=username).first()

            if user_obj:
                username = user_obj.username

            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('login')
        except Exception as e:
            print("Error in login view:", e)
            messages.error(request, f"Login error: {e}")
            return redirect('login')

    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        try:
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not username or not email or not password:
                messages.error(request, 'Please fill in all fields.')
                return render(request, 'register.html', {'username': username, 'email': email})

            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'register.html', {'username': username, 'email': email})

            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, 'Username already taken. Please choose another.')
                return render(request, 'register.html', {'username': username, 'email': email})

            if User.objects.filter(email__iexact=email).exists():
                messages.error(request, 'Email already registered. Please log in.')
                return render(request, 'register.html', {'username': username, 'email': email})

            user = User.objects.create_user(username=username, email=email, password=password)
            auth_login(request, user)

            # Send welcome registration email
            try:
                subject = f"Welcome to NEXORIG, {username}!"
                message = (
                    f"Hello {username},\n\n"
                    f"Welcome to NEXORIG! Your account has been registered successfully with email: {email}.\n\n"
                    f"Explore our latest gaming graphics cards, processors, motherboards, and PC components at unbeatable prices.\n\n"
                    f"Best regards,\n"
                    f"Team NEXORIG (jagguuopp@gmail.com)"
                )
                from_email = 'jagguuopp@gmail.com'
                recipient_list = [email]
                send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            except Exception as mail_err:
                print("Error sending registration email:", mail_err)

            return redirect('home')
        except Exception as e:
            print("Error in register view:", e)
            messages.error(request, f"Registration error: {e}")
            return render(request, 'register.html')

    return render(request, 'register.html')


def logout(request):
    try:
        auth_logout(request)
    except Exception as e:
        print("Error in logout view:", e)
    return redirect('home')


def favourites(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        favorites = Whishlist.objects.filter(user=request.user)
    except Exception as e:
        print("Error in favourites view:", e)
        favorites = []

    payload = {
        'favorites': favorites
    }
    return render(request, 'favourites.html', payload)


def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        product = Product.objects.filter(id=product_id).first()
        if product:
            item = Whishlist.objects.filter(user=request.user, product=product).first()
            if item:
                item.delete()
            else:
                Whishlist.objects.create(user=request.user, product=product)
        else:
            print("Product not found with id:", product_id)
    except Exception as e:
        print("Error in toggle_wishlist view:", e)

    next_page = request.META.get('HTTP_REFERER') or 'favourites'
    return redirect(next_page)


def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        items = CartItem.objects.filter(user=request.user)
        subtotal = 0
        total_qty = 0
        for item in items:
            subtotal += item.get_subtotal()
            total_qty += item.quantity
    except Exception as e:
        print("Error in cart view:", e)
        items = []
        subtotal = 0
        total_qty = 0

    payload = {
        'items': items,
        'cart_items': items,
        'subtotal': subtotal,
        'total': subtotal,
        'total_qty': total_qty,
    }
    return render(request, 'cart.html', payload)


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        product = Product.objects.filter(id=product_id).first()
        if product:
            cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
                cart_item.save()
        else:
            print("Product not found with id:", product_id)
    except Exception as e:
        print("Error in add_to_cart view:", e)

    return redirect('cart')


def buy_now(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        product = Product.objects.filter(id=product_id).first()
        if product:
            CartItem.objects.get_or_create(user=request.user, product=product)
        else:
            print("Product not found with id:", product_id)
    except Exception as e:
        print("Error in buy_now view:", e)

    return redirect('checkout')


def remove_from_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        product = Product.objects.filter(id=product_id).first()
        if product:
            CartItem.objects.filter(user=request.user, product=product).delete()
    except Exception as e:
        print("Error in remove_from_cart view:", e)

    return redirect('cart')


def update_cart_quantity(request, product_id, action):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        product = Product.objects.filter(id=product_id).first()
        if product:
            cart_item = CartItem.objects.filter(user=request.user, product=product).first()
            if cart_item:
                if action == 'increase':
                    cart_item.quantity += 1
                    cart_item.save()
                elif action == 'decrease':
                    cart_item.quantity -= 1
                    if cart_item.quantity <= 0:
                        cart_item.delete()
                    else:
                        cart_item.save()
    except Exception as e:
        print("Error in update_cart_quantity view:", e)

    return redirect('cart')


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # If POST submitted to checkout, process the order
    if request.method == 'POST':
        return process_checkout(request)

    items = []
    subtotal = 0
    total_qty = 0
    addresses = []

    try:
        items = CartItem.objects.filter(user=request.user)
        for item in items:
            subtotal += item.get_subtotal()
            total_qty += item.quantity

        addresses = Address.objects.filter(user=request.user).order_by('-id')
    except Exception as e:
        print("Error in checkout view:", e)

    payload = {
        'items': items,
        'subtotal': subtotal,
        'total': subtotal,
        'total_qty': total_qty,
        'addresses': addresses,
        'states': list(INDIAN_STATES_AND_CITIES.keys()),
        'states_and_cities_json': json.dumps(INDIAN_STATES_AND_CITIES),
    }
    return render(request, 'checkout.html', payload)


def process_checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return redirect('checkout')

    try:
        items = CartItem.objects.filter(user=request.user)
        if not items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('cart')

        # 1. Calculate subtotal
        subtotal = 0
        for item in items:
            subtotal += item.get_subtotal()

        chosen_address = None
        shipping_text = ""

        # 2. Check if user added a new address directly on the checkout page
        direct_house_no = request.POST.get('direct_house_no', '').strip()
        if direct_house_no:
            direct_full_name = request.POST.get('direct_full_name', '').strip() or request.user.username
            direct_phone = request.POST.get('direct_phone', '').strip()
            direct_street = request.POST.get('direct_street', '').strip()
            direct_city = request.POST.get('direct_city', '').strip()
            direct_state = request.POST.get('direct_state', '').strip()
            direct_pincode = request.POST.get('direct_pincode', '').strip()
            direct_address_type = request.POST.get('direct_address_type', 'home')

            chosen_address = Address.objects.create(
                user=request.user,
                full_name=direct_full_name,
                phone=direct_phone,
                address_line1=direct_house_no,
                address_line2=direct_street,
                city=direct_city,
                state=direct_state,
                postal_code=direct_pincode,
                country='India',
                address_type=direct_address_type
            )
        else:
            # Or use selected address from saved addresses
            selected_address_id = request.POST.get('selected_address_id')
            if selected_address_id:
                chosen_address = Address.objects.filter(id=selected_address_id, user=request.user).first()
            if not chosen_address:
                chosen_address = Address.objects.filter(user=request.user).last()

        # Build address text for the order
        if chosen_address:
            shipping_text = f"{chosen_address.full_name or request.user.username}, {chosen_address.address_line1}"
            if chosen_address.address_line2:
                shipping_text += f", {chosen_address.address_line2}"
            shipping_text += f", {chosen_address.city}, {chosen_address.state} - {chosen_address.postal_code}"
            if chosen_address.phone:
                shipping_text += f" (Ph: {chosen_address.phone})"
        else:
            shipping_text = f"{request.user.username} - Express Delivery"

        payment_method = request.POST.get('payment_method', 'COD').upper()

        # 3. Check Payment Method: Online Payment (Razorpay) vs Cash on Delivery (COD)
        if payment_method == 'COD':
            # Create confirmed order directly for Cash on Delivery
            order = Order.objects.create(
                user=request.user,
                address=chosen_address,
                shipping_address_text=shipping_text,
                payment_method='COD',
                total_amount=subtotal,
                status='Confirmed'
            )

            # Create OrderItems from cart items
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.product_name,
                    price=item.product.product_price,
                    quantity=item.quantity
                )

            # Clear cart
            CartItem.objects.filter(user=request.user).delete()

            # Send order confirmation email
            try:
                subject = f"Order Confirmation - #{order.order_id} | NEXORIG"

                items_text = ""
                for itm in order.items.all():
                    items_text += f"- {itm.product_name} x {itm.quantity} = ₹{itm.get_subtotal()}\n"

                message = (
                    f"Hello {request.user.username},\n\n"
                    f"Thank you for your order with NEXORIG!\n\n"
                    f"Order Details:\n"
                    f"• Order UUID: {order.order_id}\n"
                    f"• Payment Method: COD (Cash on Delivery)\n"
                    f"• Total Amount: ₹{order.total_amount}\n"
                    f"• Delivery Address: {order.shipping_address_text}\n\n"
                    f"Items Ordered:\n{items_text}\n"
                    f"We are preparing your hardware components with anti-static protection for express delivery.\n\n"
                    f"Best regards,\n"
                    f"Team NEXORIG (jagguuopp@gmail.com)"
                )
                from_email = 'jagguuopp@gmail.com'

                recipients = []
                if request.user.email:
                    recipients.append(request.user.email)
                if 'jagguuopp@gmail.com' not in recipients:
                    recipients.append('jagguuopp@gmail.com')

                send_mail(subject, message, from_email, recipients, fail_silently=True)
            except Exception as mail_err:
                print("Error sending order confirmation email:", mail_err)

            messages.success(request, 'Order placed successfully! Thank you for choosing NEXORIG.')
            return redirect('order_success', order_id=order.id)

        else:
            # Online Payment via Razorpay (UPI, CARD, NETBANKING)
            order = Order.objects.create(
                user=request.user,
                address=chosen_address,
                shipping_address_text=shipping_text,
                payment_method=payment_method,
                total_amount=subtotal,
                status='Pending'
            )

            # Create OrderItems
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.product_name,
                    price=item.product.product_price,
                    quantity=item.quantity
                )

            # Create order on Razorpay
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                amount_in_paise = int(subtotal * 100)

                razorpay_order = client.order.create({
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'payment_capture': '1'
                })

                order.razorpay_order_id = razorpay_order['id']
                order.save()

                # Generate a ₹100 test order for sandbox testing of Wallets and UPI if order total exceeds limits
                test_razorpay_order_id = None
                if settings.RAZORPAY_KEY_ID.startswith('rzp_test_'):
                    try:
                        test_order = client.order.create({
                            'amount': 10000, # ₹100.00 in paise
                            'currency': 'INR',
                            'payment_capture': '1',
                            'notes': {'mode': 'sandbox_wallet_test', 'actual_order_id': str(order.order_id)}
                        })
                        test_razorpay_order_id = test_order['id']
                    except Exception as te:
                        print("Razorpay sandbox test order creation notice:", te)

                # Get user phone for Razorpay UPI prefill
                user_phone = ''
                if chosen_address and chosen_address.phone:
                    user_phone = str(chosen_address.phone).strip()
                elif request.POST.get('direct_phone'):
                    user_phone = str(request.POST.get('direct_phone')).strip()
                if not user_phone:
                    user_phone = '9999999999'

                user_email = request.user.email or 'jagguuopp@gmail.com'
                user_name = ''
                if chosen_address and chosen_address.full_name:
                    user_name = chosen_address.full_name
                else:
                    user_name = request.user.get_full_name() or request.user.username

                context = {
                    'order': order,
                    'amount': amount_in_paise,
                    'currency': 'INR',
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'razorpay_order_id': razorpay_order['id'],
                    'test_razorpay_order_id': test_razorpay_order_id,
                    'test_amount': 10000,
                    'user_name': user_name,
                    'user_email': user_email,
                    'user_phone': user_phone,
                    'payment_method': payment_method,
                }
                return render(request, 'razorpay_payment.html', context)

            except Exception as rzp_err:
                print("Razorpay order creation error:", rzp_err)
                messages.error(request, f"Payment gateway error: {rzp_err}. Please try Cash on Delivery.")
                return redirect('checkout')

    except Exception as e:
        print("Error in process_checkout view:", e)
        messages.error(request, f"Error processing order: {e}")
        return redirect('checkout')


def order_success(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            messages.error(request, 'Order not found.')
            return redirect('my_orders')
    except Exception as e:
        print("Error in order_success view:", e)
        return redirect('my_orders')

    payload = {
        'order': order
    }
    return render(request, 'order_success.html', payload)


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cancel_reasons = [
        "Ordered by mistake / Changed my mind",
        "Found cheaper price elsewhere",
        "Delivery time is too long",
        "Need to change delivery address or contact number",
        "Incorrect product or specification selected",
        "Other",
    ]

    exchange_reasons = [
        "Defective or damaged component received",
        "Incompatible with my motherboard/cabinet (Wrong form factor)",
        "Received wrong item or model variant",
        "Product performance/specs not as expected",
        "Want to upgrade to a higher model",
        "Other",
    ]

    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    except Exception as e:
        print("Error in my_orders view:", e)
        orders = []

    payload = {
        'orders': orders,
        'cancel_reasons': cancel_reasons,
        'exchange_reasons': exchange_reasons,
    }
    return render(request, 'my_orders.html', payload)


def cancel_order(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            messages.error(request, 'Order not found.')
            return redirect('my_orders')

        if order.status == 'Cancelled':
            messages.info(request, 'This order is already cancelled.')
            return redirect('my_orders')

        if request.method == 'POST':
            reason = request.POST.get('reason', '').strip()
            custom_reason = request.POST.get('custom_reason', '').strip()
            final_reason = custom_reason if (reason == 'Other' and custom_reason) else reason

            order.status = 'Cancelled'
            order.cancellation_reason = final_reason or 'Cancelled by user'
            order.save()

            # Send cancellation email
            try:
                subject = f"Order Cancelled - #{order.order_id} | NEXORIG"

                items_text = ""
                for itm in order.items.all():
                    items_text += f"- {itm.product_name} x {itm.quantity} = ₹{itm.get_subtotal()}\n"

                message = (
                    f"Hello {request.user.username},\n\n"
                    f"Your order with NEXORIG has been cancelled.\n\n"
                    f"Cancellation Details:\n"
                    f"• Order UUID: {order.order_id}\n"
                    f"• Cancellation Reason: {order.cancellation_reason}\n"
                    f"• Total Order Amount: ₹{order.total_amount}\n"
                    f"• Payment Method: {order.payment_method}\n\n"
                    f"Items in this order:\n{items_text}\n"
                    f"If payment was already deducted, a full refund will be processed to your original payment method within 3-5 business days.\n\n"
                    f"Best regards,\n"
                    f"Team NEXORIG (jagguuopp@gmail.com)"
                )
                from_email = 'jagguuopp@gmail.com'

                # Send to buyer and store email
                recipients = []
                if request.user.email:
                    recipients.append(request.user.email)
                if 'jagguuopp@gmail.com' not in recipients:
                    recipients.append('jagguuopp@gmail.com')

                send_mail(subject, message, from_email, recipients, fail_silently=True)
            except Exception as mail_err:
                print("Error sending cancellation email:", mail_err)

            messages.success(request, f'Order #{order.id} has been cancelled successfully.')
    except Exception as e:
        print("Error in cancel_order view:", e)
        messages.error(request, f'Error cancelling order: {e}')

    return redirect('my_orders')


def exchange_order(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            messages.error(request, 'Order not found.')
            return redirect('my_orders')

        if order.status == 'Cancelled':
            messages.error(request, 'Cancelled orders cannot be exchanged.')
            return redirect('my_orders')

        if request.method == 'POST':
            reason = request.POST.get('reason', '').strip()
            custom_reason = request.POST.get('custom_reason', '').strip()
            final_reason = custom_reason if (reason == 'Other' and custom_reason) else reason

            order.status = 'Exchange Requested'
            order.exchange_reason = final_reason or 'Exchange requested by user'
            order.save()

            # Send exchange request email
            try:
                subject = f"Exchange Request - #{order.order_id} | NEXORIG"
                message = (
                    f"Hello {request.user.username},\n\n"
                    f"We have received your exchange request for Order #{order.order_id}.\n\n"
                    f"Exchange Details:\n"
                    f"• Reason: {order.exchange_reason}\n"
                    f"• Total Order Amount: ₹{order.total_amount}\n\n"
                    f"Our technical and support team will contact you within 24 hours to organize the replacement.\n\n"
                    f"Best regards,\n"
                    f"Team NEXORIG (jagguuopp@gmail.com)"
                )
                from_email = 'jagguuopp@gmail.com'
                recipients = []
                if request.user.email:
                    recipients.append(request.user.email)
                if 'jagguuopp@gmail.com' not in recipients:
                    recipients.append('jagguuopp@gmail.com')

                send_mail(subject, message, from_email, recipients, fail_silently=True)
            except Exception as mail_err:
                print("Error sending exchange email:", mail_err)

            messages.success(request, f'Exchange request for Order #{order.id} submitted! Our support team will process it.')
    except Exception as e:
        print("Error in exchange_order view:", e)
        messages.error(request, f'Error submitting exchange request: {e}')

    return redirect('my_orders')


def addresses(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        if request.method == 'POST':
            # Handle adding new address from the addresses page
            full_name = request.POST.get('full_name', '').strip() or request.user.username
            phone = request.POST.get('phone', '').strip()
            house_no = request.POST.get('house_no', '').strip()
            street = request.POST.get('street', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            address_type = request.POST.get('address_type', 'home')

            if house_no and city and state:
                Address.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address_line1=house_no,
                    address_line2=street,
                    city=city,
                    state=state,
                    postal_code=pincode,
                    country='India',
                    address_type=address_type
                )
                messages.success(request, 'Address added successfully!')
            else:
                messages.error(request, 'Please fill in all required address fields.')
            return redirect('addresses')

        addresses_list = Address.objects.filter(user=request.user).order_by('-id')
    except Exception as e:
        print("Error in addresses view:", e)
        addresses_list = []

    payload = {
        'addresses': addresses_list,
        'states': list(INDIAN_STATES_AND_CITIES.keys()),
        'states_and_cities_json': json.dumps(INDIAN_STATES_AND_CITIES),
    }
    return render(request, 'addresses.html', payload)


def remove_address(request, address_id):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        Address.objects.filter(id=address_id, user=request.user).delete()
        messages.success(request, 'Address removed successfully!')
    except Exception as e:
        print("Error in remove_address view:", e)
        messages.error(request, 'Could not remove address.')

    next_page = request.META.get('HTTP_REFERER') or 'addresses'
    return redirect(next_page)


def add_address(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        if request.method == 'POST':
            full_name = request.POST.get('full_name', '').strip() or request.user.username
            phone = request.POST.get('phone', '').strip()
            house_no = request.POST.get('house_no', '').strip()
            street = request.POST.get('street', '').strip()
            city = request.POST.get('city', '').strip()
            state = request.POST.get('state', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            address_type = request.POST.get('address_type', 'home')

            Address.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address_line1=house_no,
                address_line2=street,
                city=city,
                state=state,
                postal_code=pincode,
                country='India',
                address_type=address_type
            )
            messages.success(request, 'Delivery address saved successfully!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'addresses'
            return redirect(next_url)
    except Exception as e:
        print("Error in add_address view:", e)
        messages.error(request, f"Error saving address: {e}")

    payload = {
        'states': list(INDIAN_STATES_AND_CITIES.keys()),
        'states_and_cities_json': json.dumps(INDIAN_STATES_AND_CITIES),
    }
    return render(request, 'add_address.html', payload)





@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
        if not order and settings.RAZORPAY_KEY_ID.startswith('rzp_test_'):
            # Check if this was a sandbox test order
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                rzp_ord = client.order.fetch(razorpay_order_id)
                actual_uuid = rzp_ord.get('notes', {}).get('actual_order_id')
                if actual_uuid:
                    order = Order.objects.filter(order_id=actual_uuid).first()
            except Exception as fe:
                print("Error looking up test order:", fe)

        if not order:
            messages.error(request, "Order not found.")
            return redirect('checkout')

        # Verify signature with Razorpay SDK
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature(params_dict)

            # Signature matches - complete the order
            order.status = 'Confirmed'
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()

            # Clear cart
            CartItem.objects.filter(user=order.user).delete()

            # Send order confirmation email
            try:
                subject = f"Order Confirmation - #{order.order_id} | NEXORIG"
                message = (
                    f"Hello {order.user.username},\n\n"
                    f"Thank you for your payment and order with NEXORIG!\n\n"
                    f"Payment Details:\n"
                    f"• Order UUID: {order.order_id}\n"
                    f"• Razorpay Payment ID: {order.razorpay_payment_id}\n"
                    f"• Payment Method: {order.payment_method} (Online/UPI)\n"
                    f"• Total Amount: ₹{order.total_amount}\n"
                    f"• Delivery Address: {order.shipping_address_text}\n\n"
                    f"We are preparing your hardware components with anti-static protection for express delivery.\n\n"
                    f"Best regards,\n"
                    f"Team NEXORIG (jagguuopp@gmail.com)"
                )
                from_email = 'jagguuopp@gmail.com'
                recipients = []
                if order.user.email:
                    recipients.append(order.user.email)
                if 'jagguuopp@gmail.com' not in recipients:
                    recipients.append('jagguuopp@gmail.com')

                send_mail(subject, message, from_email, recipients, fail_silently=True)
            except Exception as mail_err:
                print("Error sending order confirmation email:", mail_err)

            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('order_success', order_id=order.id)

        except razorpay.errors.SignatureVerificationError:
            order.status = 'Cancelled'
            order.save()
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('checkout')

    return redirect('checkout')



client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_info':
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()

            request.user.email = email
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

        elif action == 'change_password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif len(new_password) < 6:
                messages.error(request, 'New password must be at least 6 characters.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                auth_login(request, request.user)
                messages.success(request, 'Password changed successfully!')
            return redirect('profile')

    total_orders = Order.objects.filter(user=request.user).count()
    wishlist_count = Whishlist.objects.filter(user=request.user).count()
    cart_count = CartItem.objects.filter(user=request.user).count()
    address_count = Address.objects.filter(user=request.user).count()
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'total_orders': total_orders,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
        'address_count': address_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'profile.html', context)


def admin_dashboard(request):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('login')

    try:
        # 1. Financial & Order Stats
        total_revenue = Order.objects.exclude(status='Cancelled').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = Order.objects.count()
        confirmed_orders = Order.objects.filter(status='Confirmed').count()
        delivered_orders = Order.objects.filter(status='Delivered').count()
        processing_orders = Order.objects.filter(status='Processing').count()
        cancelled_orders = Order.objects.filter(status='Cancelled').count()
        exchange_orders = Order.objects.filter(status='Exchange Requested').count()

        # 2. Products & Inventory Stats
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(product_quantity_in_stock__lte=5).count()

        # 3. Customer & Enquiry Stats
        total_users = User.objects.filter(is_staff=False).count()
        total_enquiries = Enquiry.objects.count()
        pending_enquiries = Enquiry.objects.filter(status='Pending').count()

        # 4. Data Lists
        recent_orders = Order.objects.select_related('user').all().order_by('-created_at')[:15]
        enquiries_list = Enquiry.objects.all().order_by('-created_at')
        products_list = Product.objects.select_related('product_category').all().order_by('-product_created_at')[:15]

        payload = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'confirmed_orders': confirmed_orders,
            'delivered_orders': delivered_orders,
            'processing_orders': processing_orders,
            'cancelled_orders': cancelled_orders,
            'exchange_orders': exchange_orders,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'total_users': total_users,
            'total_enquiries': total_enquiries,
            'pending_enquiries': pending_enquiries,
            'recent_orders': recent_orders,
            'enquiries_list': enquiries_list,
            'products_list': products_list,
        }
        return render(request, 'admin_dashboard.html', payload)

    except Exception as e:
        print("Error in admin_dashboard view:", e)
        messages.error(request, f"Error loading admin dashboard: {e}")
        return redirect('home')


def contact_us(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            subject = request.POST.get('subject', '').strip()
            message = request.POST.get('message', '').strip()

            if not name or not email or not subject or not message:
                messages.error(request, 'Please fill in all required fields.')
                return render(request, 'contact_us.html', {
                    'name': name, 'email': email, 'phone': phone, 'subject': subject, 'message': message
                })

            # Create enquiry
            enquiry = Enquiry.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message,
                status='Pending'
            )

            # Send email notification
            try:
                email_subject = f"New Customer Enquiry - #{enquiry.id}: {subject} | NEXORIG"
                email_body = (
                    f"Hello Administrator,\n\n"
                    f"A new customer enquiry has been submitted on NEXORIG:\n\n"
                    f"• Enquiry ID: #{enquiry.id}\n"
                    f"• Customer Name: {name}\n"
                    f"• Email: {email}\n"
                    f"• Phone: {phone or 'Not provided'}\n"
                    f"• Subject: {subject}\n\n"
                    f"Message:\n{message}\n\n"
                    f"You can view and manage this in your Admin Dashboard:\n"
                    f"http://127.0.0.1:8000/admin-dashboard/\n\n"
                    f"Best regards,\n"
                    f"NEXORIG System"
                )
                send_mail(email_subject, email_body, 'jagguuopp@gmail.com', ['jagguuopp@gmail.com'], fail_silently=True)
            except Exception as mail_err:
                print("Error sending enquiry email:", mail_err)

            messages.success(request, 'Thank you! Your enquiry has been received. Our team will contact you soon.')
            return redirect('contact_us')

    except Exception as e:
        print("Error in contact_us view:", e)
        messages.error(request, f"Error submitting enquiry: {e}")

    default_name = ''
    default_email = ''
    if request.user.is_authenticated:
        default_name = request.user.get_full_name() or request.user.username
        default_email = request.user.email

    return render(request, 'contact_us.html', {
        'default_name': default_name,
        'default_email': default_email,
    })


def update_enquiry_status(request, enquiry_id):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied.')
        return redirect('login')

    try:
        enquiry = Enquiry.objects.filter(id=enquiry_id).first()
        if not enquiry:
            messages.error(request, 'Enquiry not found.')
            return redirect('admin_dashboard')

        new_status = request.POST.get('status') or request.GET.get('status')
        if new_status in ['Pending', 'In Progress', 'Resolved']:
            enquiry.status = new_status
            enquiry.save()
            messages.success(request, f"Enquiry #{enquiry.id} marked as '{new_status}'.")
    except Exception as e:
        print("Error in update_enquiry_status view:", e)
        messages.error(request, f"Error updating enquiry: {e}")

    return redirect('admin_dashboard')


def custom_pc_build(request):
    try:
        custom_category = Category.objects.filter(category_slug='custom-pc-build-parts').first()
        parts_data = get_builder_parts()

        payload = {
            'custom_category': custom_category,
            **parts_data
        }
        return render(request, 'custom_pc_build.html', payload)

    except Exception as e:
        print("Error in custom_pc_build view:", e)
        messages.error(request, f"Error opening PC Builder: {e}")
        return redirect('home')


def add_custom_build_to_cart(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to add your custom PC build to your cart.')
        return redirect('login')

    if request.method == 'POST':
        part_keys = ['cpu', 'motherboard', 'gpu', 'ram', 'storage', 'psu', 'cabinet', 'cooler']
        added_count = 0

        for key in part_keys:
            pid = request.POST.get(key)
            if pid and str(pid).isdigit():
                prod = Product.objects.filter(id=int(pid)).first()
                if prod:
                    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=prod)
                    if not created:
                        cart_item.quantity += 1
                        cart_item.save()
                    added_count += 1

        if added_count > 0:
            messages.success(request, f"Awesome! {added_count} custom build components were added to your cart.")
            return redirect('cart')
        else:
            messages.warning(request, "Please select at least one component for your custom build.")
            return redirect('custom_pc_build')

    return redirect('custom_pc_build')



@csrf_exempt
@require_POST
def ai_parts_chat(request):
    user = request.user
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get("message", "").strip()
        chat_history = data.get("history", [])
        if not user_message:
            return JsonResponse({"reply": "Please type a message so I can help you find hardware!"})

        ai_reply = get_ai_parts(user_prompt=user_message, chat_history=chat_history, user=user)
        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        print("Error in ai_parts_chat:", e)
        return JsonResponse({"reply": "Sorry, I ran into an issue finding hardware right now. Please try again!"})
