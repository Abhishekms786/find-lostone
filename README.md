# 🎓 FindIt – Smart Campus Lost & Found System

A modern, full-stack college web application designed for campus communities to report, search, and reclaim lost and found belongings.

Built with **Python (Flask)**, **MongoDB NoSQL**, modern **CSS3 Design System**, and **Vanilla JavaScript**.

---

## 🌟 Key Features

### 🔍 For Students & Campus Members
- **Browse & Search**: Real-time search with regex escaping, filtering by status (*Lost* / *Found*), category (Electronics, Wallets, IDs, Books, etc.), and campus locations.
- **Report Items**: Dedicated submission workflows for lost and found belongings with title, category, location, date, contact info, and optional image preview.
- **Claim Verification Flow**: Interactive claiming system where students can submit proof of ownership to the finder.
- **Personal Dashboard**: Track reported items, view claim requests, and respond to claims (*Accept* / *Reject*).
- **Authentication & Security**: Secure registration and login with salted password hashing (`werkzeug.security`) and permanent session management.

### 🛡️ For Campus Administrators
- **Admin Control Panel**: Full overview of campus lost & found activity with live metrics and counters.
- **Moderation Tools**: Delete inappropriate posts or resolve duplicate listings.
- **User Management**: View registered campus users and delete spam accounts.
- **Seed Data Script**: Easily reset and seed demonstration items for viva evaluations and presentations.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask 3.1, Werkzeug, python-dotenv |
| **Database** | MongoDB NoSQL (`findit_db`) — supports Local MongoDB Community Server and MongoDB Atlas Cloud |
| **Database Driver** | PyMongo 4+ |
| **Frontend** | Jinja2 Templates, Semantic HTML5, Glassmorphism CSS3, Vanilla JS |
| **Testing** | Pytest (13 automated test suites) |

---

## 🗄️ MongoDB NoSQL Database Architecture

The application uses **MongoDB** as a document-oriented NoSQL database. No SQL or relational tables are used.

### Database Name: `findit_db`

### Collections:
1. **`users`**:
   - `_id`: ObjectId (Primary key)
   - `name`: String
   - `email`: String (Unique index)
   - `password_hash`: String (PBKDF2-SHA256 salted hash)
   - `role`: String (`'student'` or `'admin'`)
   - `created_at`: DateTime

2. **`items`**:
   - `_id`: ObjectId (Primary key)
   - `title`: String
   - `description`: String
   - `type`: String (`'lost'` or `'found'`)
   - `category`: String (Electronics, Wallets, IDs, Books, etc.)
   - `location`: String (Campus building / zone)
   - `date_lost_found`: DateTime
   - `image_url`: String (optional)
   - `status`: String (`'active'`, `'claimed'`, `'returned'`)
   - `created_by`: ObjectId (Reference to `users._id`)
   - `created_at`: DateTime
   - `updated_at`: DateTime

3. **`claims`**:
   - `_id`: ObjectId (Primary key)
   - `item_id`: ObjectId (Reference to `items._id`)
   - `requester_id`: ObjectId (Reference to `users._id`)
   - `message`: String (Proof of ownership)
   - `status`: String (`'pending'`, `'accepted'`, `'rejected'`)
   - `created_at`: DateTime

---

## 📁 Project Structure

```text
find-lostone/
├── app.py                  # Core Flask backend with routes, auth, claim workflows & API
├── seed_data.py            # Automated demo data generator with sample items & test users
├── test_app.py             # Pytest automated test suite covering all 13 core requirements
├── requirements.txt        # Python package dependencies
├── .env.example            # Template for environment configuration
├── .gitignore              # Ignored files (venv, .env, __pycache__)
├── README.md               # Complete project documentation
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

## 🚀 Setup & Installation Guide

### 1. Prerequisites
- Python 3.10 or higher
- MongoDB (Choose either **Local MongoDB** or **MongoDB Atlas Cloud**)

---

### 2. Configure MongoDB

#### Option A: Local MongoDB Community Server
If you have MongoDB installed locally on your computer:
1. Ensure the MongoDB service is running (default port `27017`).
2. In your `.env` file, set:
   ```ini
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=findit_db
   ```

#### Option B: MongoDB Atlas Cloud Database (Free Tier)
To connect to MongoDB in the cloud:
1. Sign up for a free account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free **M0 Sandbox** cluster.
3. Under **Database Access**, create a user with a username and password (e.g. `findit_user` / `YourSecurePassword123`).
4. Under **Network Access**, click **Add IP Address** and select **Allow Access from Anywhere** (`0.0.0.0/0`).
5. Click **Connect** -> **Drivers** (Python), and copy the SRV URI:
   ```ini
   MONGO_URI=mongodb+srv://findit_user:YourSecurePassword123@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=findit_db
   ```
6. Paste this URI into your `.env` file.

---

### 3. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/Abhishekms786/find-lostone.git
cd find-lostone

# Create and activate virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure your `.env` file contains:
```ini
SECRET_KEY=dev-secret-key-findit-super-secure-token-2026
MONGO_URI=mongodb://localhost:27017/
DB_NAME=findit_db
ADMIN_EMAIL=admin@findit.edu
ADMIN_PASSWORD=Admin@1234
FLASK_DEBUG=True
PORT=5000
```

### 6. Seed Sample Data (Optional for Demo)
To populate 8 sample campus items and demo student accounts:
```bash
python seed_data.py
```

### 7. Run the Application
```bash
python app.py
```
Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 🔑 Demo Credentials

| Role | Email | Password | Access |
|---|---|---|---|
| **Student 1** | `alice@college.edu` | `Password1` | Student Dashboard & Posting |
| **Student 2** | `bob@college.edu` | `Password1` | Student Dashboard & Claiming |
| **Admin** | `admin@findit.edu` | `Admin@1234` | Full Admin Control Panel (`/admin`) |

---

## 🧪 Automated Testing

The project includes 13 automated test suites covering all core workflows:
```bash
python -m pytest test_app.py -v
```

### Test Coverage:
1. `test_1_user_registration`: Mismatch validation, new account creation.
2. `test_2_login_and_logout`: Authentication, session verification, logout.
3. `test_3_create_lost_item`: Creating a lost item and verifying database record.
4. `test_4_create_found_item`: Creating a found item and verifying database record.
5. `test_5_search_items`: Full-text search and special character escaping.
6. `test_6_category_filtering`: Category selection and type filtering.
7. `test_7_item_details_page`: Details view and metadata rendering.
8. `test_8_claim_request_submission`: Non-owner claim submission.
9. `test_9_claim_acceptance_and_rejection`: Owner accepting a claim, auto-marking item as claimed.
10. `test_10_item_status_update`: Updating item status to returned.
11. `test_11_admin_login`: Administrator authentication and portal access.
12. `test_12_admin_permissions_protection`: Preventing unauthorized student access to admin routes.
13. `test_13_mongodb_persistence`: Direct NoSQL CRUD operations and collection verification.

---

## 🌐 Deployment Instructions

### Deploy to Render / Railway:
1. Push your repository to GitHub.
2. Connect your repository on Render or Railway.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Add Environment Variables:
   - `MONGO_URI`: Your MongoDB Atlas connection string
   - `SECRET_KEY`: A strong random string
   - `DB_NAME`: `findit_db`
   - `ADMIN_EMAIL`: `admin@findit.edu`
   - `ADMIN_PASSWORD`: Your chosen admin password

---

## 📸 Screenshots Overview

- **Homepage**: Hero banner with live stats counter and recent lost/found listings.
- **Browse Catalog**: Filter sidebar by category, status, campus location, and search.
- **Item Details**: Photos, description, metadata pins, and ownership claim form.
- **Student Dashboard**: Reported items table, incoming claims list with Accept/Reject actions.
- **Admin Control Panel**: Campus overview metrics, moderation tools, and user management.

---

## 🛡️ License
Open source for educational and campus community use.
