# 🎓 FindIt – Smart Campus Lost & Found System

A modern, full-stack web application designed for college campuses to help students, faculty, and administrators report, track, and reclaim lost and found belongings.

Built with **Python (Flask)**, **MongoDB**, modern **CSS3 Design System**, and **Vanilla JavaScript**.

---

## 🌟 Key Features

### 🔍 For Students & Campus Members
- **Browse & Search**: Real-time filtering by status (*Lost* / *Found*), category (Electronics, Wallets, IDs, Books, etc.), and campus locations.
- **Report Items**: Easy submission form with item descriptions, categories, campus location pins, date lost/found, contact details, and optional image preview.
- **Claim Verification Flow**: Secure claiming system where students can submit proof of ownership to the finder.
- **Personal Dashboard**: Track all your reported items, view claim requests, and respond to claims (Accept / Reject).
- **Authentication & Security**: Secure registration and login with salted password hashing (`werkzeug.security`) and session management.

### 🛡️ For Campus Administrators
- **Admin Control Panel**: Full overview of campus lost & found activity with live metrics.
- **Moderation Tools**: Delete inappropriate posts or resolve duplicate listings.
- **User Management**: Manage registered campus users and maintain platform integrity.
- **Seed Data Script**: Easily reset and seed demonstration items for vivas, project presentations, and evaluations.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask 3.0, Werkzeug, python-dotenv |
| **Database** | MongoDB (Local MongoDB Community Server or MongoDB Atlas cloud) |
| **Database Driver** | PyMongo 4+ |
| **Frontend** | Jinja2 Templates, Semantic HTML5, Custom Glassmorphism CSS3, Vanilla JS |
| **Testing** | Pytest |

---

## 📁 Project Structure

```text
find-lostone/
├── app.py                  # Core Flask backend with routes, auth, claim workflows & API
├── seed_data.py            # Automated demo data generator with sample items & test users
├── test_app.py             # Pytest automated test suite covering all core features
├── requirements.txt        # Python package dependencies
├── .env.example            # Template for environment configuration
├── .gitignore              # Ignored files (venv, .env, __pycache__)
├── static/
│   ├── css/
│   │   └── style.css       # Complete modern CSS design system & responsive layout
│   └── js/
│       └── app.js          # Interactive UX (counters, modal confirmation, claim UI)
└── templates/
    ├── base.html           # Master layout with responsive navbar, flash alerts & footer
    ├── index.html          # Hero section, live counter stats & recent lost/found listings
    ├── browse.html         # Filterable catalog with search bar and category tabs
    ├── _item_card.html     # Reusable item card component
    ├── item_details.html   # Detailed view with claim submission and owner actions
    ├── create_item.html    # Form to post a new lost or found item
    ├── edit_item.html      # Update item information
    ├── dashboard.html      # User dashboard with tabs for reported items & incoming claims
    ├── login.html          # Clean card-based login screen
    ├── register.html       # Student registration with validation
    ├── admin.html          # Dedicated campus administrator management portal
    ├── 404.html            # User-friendly 404 error page
    └── error.html          # Generic server error page
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher
- MongoDB installed locally or a free MongoDB Atlas connection string

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Abhishekms786/find-lostone.git
cd find-lostone

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration works immediately with local MongoDB:
```ini
SECRET_KEY=dev-secret-key-findit-super-secure-token-2026
MONGO_URI=mongodb://localhost:27017/
DB_NAME=findit_db
ADMIN_EMAIL=admin@findit.edu
ADMIN_PASSWORD=Admin@1234
FLASK_DEBUG=True
PORT=5000
```

### 5. Seed Sample Data (Optional for Demo)
To populate 8 sample campus items and demo student accounts:
```bash
python seed_data.py
```

Demo Credentials:
- **Student 1**: `alice@college.edu` / `Password1`
- **Student 2**: `bob@college.edu` / `Password1`
- **Admin**: `admin@findit.edu` / `Admin@1234`

### 6. Run the Application
```bash
python app.py
```
Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Running Automated Tests
Run the pytest test suite to verify all endpoints and flows:
```bash
python -m pytest test_app.py -v
```

---

## 🛡️ License
Open source for educational and campus community use.
