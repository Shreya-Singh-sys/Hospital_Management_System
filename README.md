🏥 Hospital Management System (HMS)

A comprehensive web application designed to streamline hospital operations by integrating Admin, Doctor, and Patient workflows into a single, cohesive platform. Built with Flask, SQLite, and a modern Glassmorphism UI.

🚀 Project Overview

The Hospital Management System addresses the challenges of manual record-keeping and disconnected software by providing a centralized solution. It enables seamless scheduling, conflict-free appointment booking, and secure medical record tracking.

Key Features:

Role-Based Access Control (RBAC): Distinct dashboards for Admins, Doctors, and Patients.

Smart Scheduling: Prevents double-booking and allows doctors to set weekly availability.

Medical History: Digital storage of diagnoses, treatments, and prescriptions.

Modern UI: Responsive, beautiful Glassmorphism design using Bootstrap 5.

🛠️ Tech Stack

Backend: Python, Flask

Database: SQLite (SQLAlchemy ORM)

Frontend: HTML5, CSS3, Bootstrap 5, Jinja2

Authentication: Flask-Login (Secure session management)

✨ Features by Role

👨‍💼 Admin (Hospital Staff)

Dashboard: Real-time stats (Total Doctors, Patients, Appointments).

Doctor Management: Add new doctors via popup modal, edit profiles, and delete users.

User Control: Blacklist/Block users to restrict access.

Appointment Oversight: View full appointment history with options to cancel or delete records.

Search & Filter: Find doctors by name or department specialization.

👨‍⚕️ Doctor

My Appointments: View upcoming schedule sorted by date/time.

Consultation: Mark appointments as "Completed" and enter Diagnosis & Prescriptions.

Availability: Toggle availability (Available/Unavailable) for the next 7 days.

Patient History: Access past medical records of assigned patients.

🤒 Patient

Self-Registration: Sign up and manage personal profile.

Department Browser: View all hospital departments with visual banners.

Booking System: Search doctors, check availability (Green/Red indicators), and book slots.

Manage Appointments: View upcoming visits, Reschedule dates/times, or Cancel bookings.

Medical Records: Access past treatments and prescriptions provided by doctors.

📸 Screenshots

(Add your screenshots here. For example:)

Login Page: Glassmorphism design.

Admin Dashboard: Stats and User Management.

Patient Booking: Department selection and availability grid.

⚙️ Installation & Setup

Clone the Repository

git clone [https://github.com/yourusername/hospital-management-system.git](https://github.com/yourusername/hospital-management-system.git)
cd hospital-management-system


Create a Virtual Environment (Optional but Recommended)

python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


Install Dependencies

pip install -r requirements.txt


Run the Application

python app.py


The database (hospital.db) will be created automatically on the first run.

A default Admin account will be created.

Access the App
Open your browser and go to http://127.0.0.1:5000/

🔑 Default Credentials

Admin Username: admin

Admin Password: admin123
