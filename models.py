from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'doctor', 'patient'
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    is_active_user = db.Column(db.Boolean, default=True) # For Blacklisting

    # Relationships
    doctor_profile = db.relationship('DoctorProfile', backref='user', uselist=False)
    
    def get_id(self):
        return str(self.id)

class DoctorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False) # e.g. Cardiology
    license_number = db.Column(db.String(50))
    fee = db.Column(db.Float, default=500.0)
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default='Booked')  # Booked, Completed, Cancelled
    symptoms = db.Column(db.String(255))
    
    # Relationships for easy access
    patient = db.relationship('User', foreign_keys=[patient_id], backref='my_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doc_appointments')
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    
    patient = db.relationship('User', foreign_keys=[patient_id], backref='my_appointments')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doc_appointments')

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
# class Doctor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     department = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), default='Active')