## 🏥 Hospital Management System (HMS)

A comprehensive web application designed to streamline hospital operations by integrating Admin, Doctor, and Patient workflows into a single, cohesive platform. Built with Flask, SQLite, and a modern Glassmorphism UI.

## 🚀 Project Overview

The Hospital Management System addresses the challenges of manual record-keeping and disconnected software by providing a centralized solution. It enables seamless scheduling, conflict-free appointment booking, and secure medical record tracking.

### Key Features:

* **Role-Based Access Control (RBAC):** Distinct dashboards for Admins, Doctors, and Patients.

* **Smart Scheduling:** Prevents double-booking and allows doctors to set weekly availability.

* **Medical History:** Digital storage of diagnoses, treatments, and prescriptions.

* **Modern UI:** Responsive, beautiful Glassmorphism design using Bootstrap 5.

### 🛠️ Tech Stack

* **Backend:** Python, Flask

* **Database:** SQLite (SQLAlchemy ORM)

* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2

* **Authentication:** Flask-Login (Secure session management)

## ✨ Features by Role

### 👨‍💼 Admin (Hospital Staff)

* **Dashboard:** Real-time stats (Total Doctors, Patients, Appointments).

* **Doctor Management:** Add new doctors via popup modal, edit profiles, and delete users.

* **User Control:** Blacklist/Block users to restrict access.

* **Appointment Oversight:** View full appointment history with options to cancel or delete records.

* **Search & Filter:** Find doctors by name or department specialization.

### 👨‍⚕️ Doctor

* **My Appointments:** View upcoming schedule sorted by date/time.

* **Consultation:** Mark appointments as "Completed" and enter Diagnosis & Prescriptions.

* **Availability:** Toggle availability (Available/Unavailable) for the next 7 days.

* **Patient History:** Access past medical records of assigned patients.

### 🤒 Patient

* **Self-Registration:** Sign up and manage personal profile.

* **Department Browser:** View all hospital departments with visual banners.

* **Booking System:** Search doctors, check availability (Green/Red indicators), and book slots.

* **Manage Appointments:** View upcoming visits, Reschedule dates/times, or Cancel bookings.

* **Medical Records:** Access past treatments and prescriptions provided by doctors.


