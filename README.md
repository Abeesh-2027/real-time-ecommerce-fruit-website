# 🍎 Fruitzone — Django Fruit E-Commerce Website

A full-featured, real-time **fruit e-commerce platform** built with Django, MongoDB, and Razorpay. Customers can browse fresh fruits, manage a shopping cart, and checkout with secure online payments — while admins get a powerful dashboard to manage products and orders.

## Screenshot
![image alt](https://github.com/Abeesh-2027/real-time-ecommerce-fruit-website/blob/bb82bc7033841fece6e46b5b0a1e73db1520c47e/Screenshot%20(6).png)
![image alt](https://github.com/Abeesh-2027/real-time-ecommerce-fruit-website/blob/bb82bc7033841fece6e46b5b0a1e73db1520c47e/Screenshot%20(7).png)


## ✨ Features

### 🛒 Customer Side
- Browse and search fresh fruit products
- Add to cart, update quantities, remove items
- Checkout with Razorpay (UPI, Card, Net Banking, Cash on Delivery)
- Order confirmation and success page
- Order history view

### 🔐 Authentication
- User registration and login
- Session-based authentication
- Separate admin and customer roles

### 🛠️ Admin Panel
- Add, edit, and delete products (name, price, stock, images)
- View all customer orders in real time
- Update order statuses
- Manage product categories and inventory

### 💳 Payment Integration
- Razorpay payment gateway
- Supports UPI, Card, Net Banking, and COD
- Secure order creation and payment verification
- Auto order confirmation on payment success

---

## 🧱 Tech Stack

| Layer        | Technology              |
|--------------|-------------------------|
| Backend      | Django 4.x (Python)     |
| Database     | MongoDB (via Djongo / PyMongo) |
| Payments     | Razorpay API            |
| Frontend     | HTML, CSS, JavaScript   |
| Templating   | Django Templates (Jinja-style) |
| Static Files | Django StaticFiles      |
| Auth         | Django Sessions         |

---

## 📁 Project Structure

```
fruitzone/
├── fruits/
│   ├── sales/
│   │   ├── zone/
│   │   │   ├── templates/zone/
│   │   │   │   ├── home.html
│   │   │   │   ├── login.html
│   │   │   │   ├── success.html
│   │   │   │   └── ...
│   │   │   ├── static/images/
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── admin.py
│   │   │   └── apps.py
│   │   ├── migrations/
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── db.sqlite3
├── pyvenv.cfg
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fruitzone.git
cd fruitzone/fruits
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB

Update your `settings.py` to connect to MongoDB:

```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'fruitzone',
        'CLIENT': {
            'host': 'your-mongodb-connection-string',
        }
    }
}
```

### 5. Configure Razorpay

Add your Razorpay credentials in `settings.py` or `.env`:

```python
RAZORPAY_KEY_ID = 'your_key_id'
RAZORPAY_KEY_SECRET = 'your_key_secret'
```

### 6. Apply Migrations & Create Superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 💳 Razorpay Integration

The checkout flow uses Razorpay's order API:

1. User places order → Django creates a Razorpay order via API
2. Frontend opens Razorpay payment modal
3. On success, payment signature is verified server-side
4. Order is confirmed and saved; user is redirected to `success.html`

Supported payment methods:
- UPI Payment
- Card Payment
- Net Banking
- Cash on Delivery (COD)

---

## 🔧 Admin Usage

Log in at `/admin` with superuser credentials to:

- **Products**: Add/edit/delete fruit listings with price and stock
- **Orders**: View all customer orders with items, totals, and payment method
- **Users**: Manage registered customers

---

## 🌐 Key URLs

| URL Pattern           | View              | Description              |
|-----------------------|-------------------|--------------------------|
| `/`                   | `home`            | Product listing page     |
| `/login/`             | `login`           | User login               |
| `/cart/`              | `cart`            | Shopping cart            |
| `/checkout/`          | `checkout`        | Payment & order form     |
| `/success/`           | `success`         | Order confirmation       |
| `/zone/view/`         | `zone:view`       | View all orders (admin)  |
| `/zone/product/`      | `zone:product`    | Manage products (admin)  |
| `/admin/`             | Django Admin      | Full admin panel         |

---

## 📦 Requirements

```
Django>=4.0
djongo
pymongo
razorpay
Pillow
```

> Generate `requirements.txt` with: `pip freeze > requirements.txt`

---

## 🔒 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/fruitzone
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_secret_here
```




---

> 🍊 *Fresh fruits, fast delivery, seamless checkout — Fruitzone has it all.*
