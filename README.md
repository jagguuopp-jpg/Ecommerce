# NEXORIG — Premium PC Hardware & Custom PC Builder E-Commerce Platform

A full-stack Django e-commerce platform and custom PC building web application tailored for PC enthusiasts, gamers, and professionals in India. The application features **190+ authentic hardware components**, an interactive **Custom PC Builder**, online checkout with **Razorpay**, and a **Google Gemini-powered AI Hardware Assistant** that can design compatible PC builds for any budget, compare hardware, and add components directly to the user's cart.

---

## ⚡ Tech Stack

* **Backend:** Python 3.9+, Django 4.2
* **Database:** SQLite (default / easily switchable to PostgreSQL or MySQL)
* **AI & LLM:** Google Gemini API (`google-genai` SDK using `gemini-3.5-flash-lite`)
* **Payments:** Razorpay Payment Gateway integration
* **Image Processing:** Pillow (PIL)
* **Frontend:** HTML5, CSS3, JavaScript (Dark Gaming Glassmorphic Theme)
* **Icons & Fonts:** Bootstrap Icons, Outfit typography

---

## ✨ Key Features

### 1. Extensive Catalog (190+ Components)
* **Broad Price Range:** Ranging from ₹149 accessories up to ₹32,50,000 enterprise accelerators.
* **Component Categories:**
  * **Processors (CPU):** Intel 12th/13th/14th Gen Core i3 to i9, AMD Ryzen 3000/5000/7000/9000, AMD Ryzen Threadripper PRO 7000 series (up to 96 cores), Intel Xeon W.
  * **Graphics Cards (GPU):** NVIDIA GTX 1650, RTX 3050/3060, RTX 4060 to RTX 4090, AMD Radeon RX 6600 to RX 7900 XTX, NVIDIA Workstation GPUs (RTX 4000/5000/6000 Ada, NVIDIA A100, NVIDIA H100).
  * **Motherboards:** Intel LGA1700 (H610, B660, B760, Z790), AMD AM4 (B450, B550), AMD AM5 (B650, X670E), Workstation (sTR5 WRX90 / TRX50).
  * **Memory (RAM):** DDR4 (8GB to 32GB kits) and DDR5 (16GB to 96GB consumer kits, plus up to 512GB ECC Registered Server RDIMMs).
  * **Storage (SSD & HDD):** Gen4 & Gen5 NVMe M.2 SSDs (Crucial, Kingston, Samsung, WD up to 14,500 MB/s), 7200 RPM bulk HDDs, up to 30.72TB Enterprise NVMe SSDs.
  * **Power Supplies (PSU):** 500W to 2000W 80+ Bronze, Gold, Platinum, and Titanium certified ATX 3.0 power supplies.
  * **Cabinets & Cases:** Budget mesh towers, panoramic dual-chamber glass cases, open-frame showcase cases, smart motorized desk chassis.
  * **CPU Coolers:** Compact air coolers, dual-tower heatsinks (Noctua, Thermalright, DeepCool), 240mm & 360mm ARGB LCD liquid AIO coolers, sub-ambient liquid chillers.
  * **Accessories & Peripherals:** Thermal pastes (Arctic MX-4, Noctua NT-H1, Thermal Grizzly Kryonaut), anti-sag brackets, sleeved cables, toolkits, 240Hz OLED gaming monitors.

### 2. Custom PC Builder (`/custom-pc-build/`)
* Interactive PC configuration tool letting customers select each component (CPU, Motherboard, GPU, RAM, Storage, PSU, Cabinet, Cooler).
* Real-time price calculation and one-click bulk addition of the entire build to the shopping cart.

### 3. NEXORIG AI Assistant (`/api/ai-parts/`)
* **Floating Chat Drawer:** Available across every page on the store with persistent chat history across page navigation via `sessionStorage`.
* **Multi-Budget Build Architect:**
  * Curates 100% compatible PC builds for any budget (e.g. ₹35K budget build, ₹80K 1440p build, ₹1.8L 4K build, ₹15L Deep Learning workstation).
  * Computes accurate total prices in ₹ and formats builds into organized comparison tables.
* **Component Advice & Comparisons:** Recommends the best hardware based on user needs (gaming, video editing, 3D modeling, coding, deep learning).
* **Direct Add to Cart:**
  * When the customer asks to *"Add this build to cart"* or *"Add to cart"*, the AI automatically parses the product IDs and loads them into the user's cart (with quantity set to 1 to prevent stacking).

### 4. E-Commerce Core & User Account
* **Shopping Cart & Checkout:** Add/remove items, update quantities, calculate grand totals.
* **Wishlist:** Save favorite components with one click.
* **Address Book:** Save multiple shipping addresses with Indian states and pin codes.
* **Orders & Tracking:** View order history, download invoice details, cancel or request exchanges.
* **Razorpay Payment Gateway:** Secure online payment processing with signature verification.
* **Admin Dashboard & Enquiries:** Custom admin panel to manage product stock, track customer enquiries, and trigger email alerts.

---

## 📁 Project Structure

```
NEXORIG Website/
├── run.sh                          # Convenient bash runner script
├── requirements.txt                # Python project dependencies
├── README.md                       # Documentation
├── .venv/                          # Python virtual environment
└── Pc_store/                       # Main Django Project root
    ├── manage.py                   # Django CLI tool
    ├── db.sqlite3                  # SQLite database with 193 components
    ├── Pc_store/                   # Project settings and URL routing
    │   ├── settings.py             # Settings (Static, Media, API Keys)
    │   ├── urls.py                 # Root URL configuration
    │   └── wsgi.py
    ├── media/                      # User-uploaded & product image assets
    │   └── products/               # High-quality images for all 193 parts
    └── store/                      # Main application
        ├── models.py               # Models (Category, Product, CartItem, Order, etc.)
        ├── views.py                # Views (Catalog, PC Builder, Cart, Auth, AI Chat)
        ├── urls.py                 # Store URL patterns
        ├── AI.py                   # Gemini AI Assistant integration
        ├── static/                 # Static CSS, JS, and image assets
        │   └── css/
        │       ├── ai_assistant.css # AI Chatbot styling
        │       └── dropdown.css     # Navbar dropdown styling
        └── templates/              # HTML Templates
            ├── layout.html         # Base template with Navbar, Footer & AI Widget
            ├── home.html           # Homepage product listing & hero banner
            ├── custom_pc_build.html# Interactive custom PC builder
            ├── cart.html           # Shopping cart
            ├── checkout.html       # Checkout & Razorpay payment screen
            ├── my_orders.html      # Customer orders page
            ├── admin_dashboard.html# Staff administration dashboard
            └── ...
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
* Python 3.9 or higher installed
* macOS, Linux, or Windows with terminal access

### 2. Activate Virtual Environment
Navigate to the project root directory and activate the included virtual environment:

```bash
cd "NEXORIG Website"
source .venv/bin/activate
```

*(On Windows PowerShell, use `.venv\Scripts\Activate.ps1`)*

### 3. Install Dependencies
If installing on a new machine:
```bash
pip install -r requirements.txt
```

### 4. Environment Variables & API Keys
Open `Pc_store/Pc_store/settings.py` and verify your API credentials:
* **Gemini API Key:**
  ```python
  GEMINI_API_KEY = "your-google-gemini-api-key"
  ```
* **Razorpay Keys:**
  ```python
  RAZORPAY_KEY_ID = "rzp_test_..."
  RAZORPAY_KEY_SECRET = "your-razorpay-secret"
  ```

### 5. Run Database Migrations (Optional)
The included `db.sqlite3` already comes fully migrated and pre-populated with 193 products:
```bash
cd Pc_store
python manage.py migrate
```

### 6. Start the Development Server
You can simply run the provided launch script from the root folder:
```bash
./run.sh
```
Or run manage.py directly:
```bash
cd Pc_store
python manage.py runserver 8000
```

Open your browser and visit:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 💬 How to Use the AI Assistant

1. Click the glowing **AI Assistant** pill button at the bottom-right of any page.
2. Ask questions such as:
   * *"Recommend a budget gaming PC under 40000 rs"*
   * *"I want a 1440p gaming build for 1.2 lakh with RTX 4070"*
   * *"Suggest a Deep Learning AI workstation around 10 to 12 lakhs"*
   * *"What is the cheapest thermal paste you have?"*
   * *"Compare RTX 4060 vs RX 7600 XT"*
3. To add the recommended build or part to your cart:
   * Simply reply: **"Add this build to cart"** or **"Add to cart"**.
   * The AI will instantly save the items to your cart and display a direct checkout button!

---

## 🛠️ Code Design & Philosophy
All code in this project follows **simple, readable, and standard Django & Python practices**:
* No unnecessary complexity, micro-frameworks, or difficult regex layers.
* Clear database querying using Django's native ORM.
* Safe CSRF-handled JSON endpoints with instant responsive feedback.
* Robust fallback handling so the site remains operational even if network or third-party APIs are temporarily unavailable.

---

## 📄 License
This project is developed for educational and retail demonstration purposes. All product trademarks, model names, and brand logos belong to their respective manufacturers.
