import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from .models import Fruit, Order, OrderItem

logger = logging.getLogger(__name__)

PRODUCTS_PREVIEW = [
    {'name': 'Apple',       'img': 'images/apple.jpg'},
    {'name': 'Pomegranate', 'img': 'images/pomegranate.jpg'},
    {'name': 'Mango',       'img': 'images/mango.jpg'},
    {'name': 'Orange',      'img': 'images/orange.jpg'},
]

STATIC_PRODUCTS = [
    {'name': 'Apple',       'price': 120, 'image': 'apple.jpg'},
    {'name': 'Pomegranate', 'price': 180, 'image': 'pomegranate.jpg'},
    {'name': 'Mango',       'price': 100, 'image': 'mango.jpg'},
    {'name': 'Orange',      'price': 80,  'image': 'orange.jpg'},
    {'name': 'Banana',      'price': 60,  'image': 'morais.jpg'},
    {'name': 'Grapes',      'price': 140, 'image': 'grapes.jpg'},
    {'name': 'Pineapple',   'price': 90,  'image': 'pineapple.jpg'},
    {'name': 'Watermelon',  'price': 50,  'image': 'watermelon.jpg'},
]


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('zone:home')

    context = {}

    if request.method == 'POST':
        action = request.POST.get('action', 'login')

        if action == 'login':
            email    = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            user     = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('zone:home')
            else:
                context.update({
                    'login_error': 'Invalid email or password. Please try again.',
                    'login_email': email,
                    'active_side': 'login',
                })

        elif action == 'signup':
            name     = request.POST.get('name', '').strip()
            email    = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            confirm  = request.POST.get('confirm', '')

            error = None
            if len(name) < 2:
                error = 'Please enter your full name.'
            elif '@' not in email:
                error = 'Please enter a valid email address.'
            elif len(password) < 6:
                error = 'Password must be at least 6 characters.'
            elif password != confirm:
                error = 'Passwords do not match.'
            elif User.objects.filter(username=email).exists():
                error = 'An account with this email already exists.'

            if error:
                context.update({
                    'signup_error': error,
                    'signup_name':  name,
                    'signup_email': email,
                    'active_side':  'signup',
                })
            else:
                parts = name.split()
                User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=parts[0],
                    last_name=' '.join(parts[1:]) if len(parts) > 1 else '',
                )
                context.update({
                    'signup_success': f'Account created! Welcome, {parts[0]}. Please log in.',
                    'login_email':    email,
                    'active_side':    'login',
                })

    return render(request, 'zone/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('zone:login')   # FIX: was redirect('login') — must use namespaced URL


# ─────────────────────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def home_view(request):
    context = {
        'products_preview': PRODUCTS_PREVIEW,
        'contact_success':  request.session.pop('contact_success', None),
        'contact_error':    request.session.pop('contact_error', None),
        'contact_name':     request.session.pop('contact_name', ''),
        'contact_email':    request.session.pop('contact_email', ''),
        'contact_message':  request.session.pop('contact_message', ''),
    }
    return render(request, 'zone/home.html', context)


@login_required
def products_view(request):
    query  = request.GET.get('q', '').strip()
    fruits = Fruit.objects.filter(is_active=True).order_by('name')
    if query:
        fruits = fruits.filter(name__icontains=query)
    return render(request, 'zone/product.html', {
        'fruits':          fruits,
        'static_products': STATIC_PRODUCTS,
        'query':           query,
    })


@login_required
def cart_view(request):
    return render(request, 'zone/cart.html')


@login_required
def checkout_view(request):
    user = request.user
    return render(request, 'zone/checkout.html', {
        'user_name':       user.get_full_name() or user.username,
        'user_email':      user.email,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })


@login_required
def success_view(request):
    return render(request, 'zone/success.html')


@login_required
def orders_view(request):
    return render(request, 'zone/orders.html')


@login_required                              # FIX: was pointing to orders_view; now its own view
def view_order_view(request):
    return render(request, 'zone/view.html')


# ─────────────────────────────────────────────────────────────────────────────
# CONTACT
# ─────────────────────────────────────────────────────────────────────────────

@require_POST
@login_required
def contact_view(request):
    name    = request.POST.get('contact_name', '').strip()
    email   = request.POST.get('contact_email', '').strip()
    message = request.POST.get('contact_message', '').strip()

    if not name or not email or not message:
        request.session['contact_error']   = 'Please fill in all fields.'
        request.session['contact_name']    = name
        request.session['contact_email']   = email
        request.session['contact_message'] = message
        return redirect('zone:home')

    if '@' not in email:
        request.session['contact_error']   = 'Please enter a valid email address.'
        request.session['contact_name']    = name
        request.session['contact_email']   = email
        request.session['contact_message'] = message
        return redirect('zone:home')

    try:
        send_mail(
            subject=f'[Fruitzone] New message from {name}',
            message=f'From: {name} <{email}>\n\n{message}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
    except Exception as exc:
        logger.warning('Contact email failed: %s', exc)

    request.session['contact_success'] = "Thank you! We'll get back to you soon. 🎉"
    return redirect('zone:home')


# ─────────────────────────────────────────────────────────────────────────────
# RAZORPAY API
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
@login_required                              # FIX: payment endpoints must require login
def razorpay_create_order(request):
    """Create a Razorpay order and return the order_id to the frontend."""
    try:
        # FIX: read body once and reuse — previously parsed twice, second parse would fail
        body   = json.loads(request.body)
        amount = int(float(body.get('amount', 0)) * 100)   # convert ₹ → paise

        try:
            import razorpay
            client   = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            rz_order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})
            razorpay_order_id = rz_order['id']

        except ImportError:
            # razorpay package not installed — return a demo order_id so checkout still works
            logger.warning('razorpay package not installed; running in demo mode.')
            razorpay_order_id = 'order_DEMO' + str(int(datetime.now().timestamp()))

        return JsonResponse({
            'success':           True,
            'razorpay_order_id': razorpay_order_id,
            'amount':            amount,
            'key':               settings.RAZORPAY_KEY_ID,
        })

    except Exception as exc:
        logger.error('Razorpay create order failed: %s', exc)
        return JsonResponse({'success': False, 'error': str(exc)}, status=400)


@csrf_exempt
@require_POST
@login_required                              # FIX: payment endpoints must require login
def razorpay_verify(request):
    """Verify Razorpay payment signature."""
    try:
        data = json.loads(request.body)

        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id':   data.get('razorpay_order_id', ''),
                'razorpay_payment_id': data.get('razorpay_payment_id', ''),
                'razorpay_signature':  data.get('razorpay_signature', ''),
            })

        except ImportError:
            logger.warning('razorpay package not installed; skipping signature check (demo mode).')

        return JsonResponse({'success': True})

    except Exception as exc:
        logger.error('Razorpay verify failed: %s', exc)
        return JsonResponse({'success': False, 'error': 'Signature verification failed'}, status=400)


# ─────────────────────────────────────────────────────────────────────────────
# ORDER API
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
@login_required                              # FIX: order placement must require login
def api_place_order(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'success': False, 'errors': {'body': ['Invalid JSON']}}, status=400)

    customer = data.get('customer', {})
    items    = data.get('items', [])
    errors   = {}

    if not customer.get('name'):    errors['name']    = ['Customer name is required.']
    if not customer.get('phone'):   errors['phone']   = ['Phone number is required.']
    if not customer.get('email'):   errors['email']   = ['Email is required.']
    if not customer.get('address'): errors['address'] = ['Delivery address is required.']
    if not items:                   errors['items']   = ['Order must have at least one item.']

    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    try:
        order = Order.objects.create(
            order_id            = data.get('id', ''),
            customer_name       = customer.get('name'),
            customer_phone      = customer.get('phone'),
            customer_email      = customer.get('email'),
            delivery_address    = customer.get('address'),
            delivery_notes      = customer.get('notes', ''),
            subtotal            = data.get('subtotal', 0),
            delivery_charge     = data.get('delivery', 0),
            total               = data.get('total', 0),
            payment_method      = data.get('payMethod', 'cod'),
            status              = data.get('status', 'confirmed'),
            razorpay_payment_id = (data.get('razorpay') or {}).get('payment_id', ''),
        )
        for item in items:
            OrderItem.objects.create(
                order     = order,
                name      = item.get('name', ''),
                price     = item.get('price', 0),
                quantity  = item.get('qty', 1),
                image_url = item.get('img', ''),
            )
        return JsonResponse({'success': True, 'order_id': order.order_id}, status=201)

    except Exception as exc:
        logger.error('Order save failed: %s', exc)
        return JsonResponse({'success': False, 'warning': 'Saved locally only.'}, status=200)