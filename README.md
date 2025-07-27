# 🩸 Blood Donation Management System

This is a **Blood Donation Management System** built using **Python Flask** and **SQLite** that helps manage donor registrations, hospital blood requests, admin management, and blood availability tracking.

## 🚀 Features

- **User Roles:** Admin, Donor, and Hospital (Requestor)
- **Signup/Login System:** Role-based login for admin, donor, and hospital
- **Donor Module:**
  - Register donor details
  - View donor information
- **Hospital Module:**
  - Submit blood requests
  - View request history
- **Admin Module:**
  - Dashboard with access to all data
  - View registered donors and hospital requests
  - Monitor blood availability by type

## 🛠️ Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS (via Jinja2 templates)
- **Database:** SQLite
- **Security:** Passwords are securely hashed using `werkzeug.security`


## ⚙️ Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/blood-donation-system.git
   cd blood-donation-system

  **Create and activate a virtual environment :**

 -python -m venv venv
  -source venv/bin/activate  # On Windows: venv\Scripts\activate
## install requirements
 -pip install -r requirements.txt
## Run the Flask app
 -python app.py


