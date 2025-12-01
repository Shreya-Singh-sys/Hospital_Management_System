from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, DoctorProfile, Appointment, Availability
from datetime import datetime, timedelta
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Hardcoded Department Descriptions ---
DEPT_DESCRIPTIONS = {
    "General": "Primary care for common health issues and routine checkups.",    
    "Cardiology": "Cardiology deals with the disorders of the heart as well as some parts of the circulatory system.",
    "Neurology": "Neurology deals with the diagnosis and treatment of conditions involving the nervous system.",
    "Pediatrics": "Pediatrics focuses on the health and medical care of infants, children, and adolescents.",
    "Orthopedics": "Orthopedics focuses on injuries and diseases of your body's musculoskeletal system.",
    "Radiology": "Radiology uses medical imaging to diagnose and treat diseases.",
    "Oncology": "Oncology deals with the prevention, diagnosis, and treatment of cancer."
}
DEPT_IMAGES = {
    "General": "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?q=80&w=2091&auto=format&fit=crop",
    "Cardiology": "https://images.unsplash.com/photo-1628348068343-c6a848d2b6dd?q=80&w=2000&auto=format&fit=crop",
    "Neurology": "https://plus.unsplash.com/premium_photo-1676325101995-cd28b7952e47?q=80&w=2000&auto=format&fit=crop",
    "Pediatrics": "https://images.unsplash.com/photo-1516627145497-ae6968895b74?q=80&w=2000&auto=format&fit=crop",
    "Orthopedics": "https://images.unsplash.com/photo-1583912267652-3c6ebf2162eb?q=80&w=2000&auto=format&fit=crop",
    "Radiology": "https://images.unsplash.com/photo-1516549655169-df83a0a836d8?q=80&w=2000&auto=format&fit=crop",
    "Oncology": "https://images.unsplash.com/photo-1579154204601-01588f351e67?q=80&w=2000&auto=format&fit=crop"
}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database & Admin Initialization ---
with app.app_context():
    db.create_all()
    # Programmatically create admin if not exists
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin', name='Super Admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin account created successfully.")

# =========================================
# AUTHENTICATION ROUTES
# =========================================

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin_dashboard'))
        if current_user.role == 'doctor': return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('patient_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_active_user:
                flash('Your account has been blacklisted. Contact Admin.', 'danger')
                return redirect(url_for('login'))
            login_user(user)
            if user.role == 'admin': return redirect(url_for('admin_dashboard'))
            if user.role == 'doctor': return redirect(url_for('doctor_dashboard'))
            return redirect(url_for('patient_dashboard'))
        flash('Invalid Credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(username=username).first():
            flash('Username exists', 'warning')
            return redirect(url_for('register'))
            
        user = User(name=name, username=username, password=generate_password_hash(password), role=role)
        
        # If registering as doctor (rare, usually admin adds them), create profile
        if role == 'doctor':
            db.session.add(user)
            db.session.commit()
            profile = DoctorProfile(user_id=user.id, department="General", license_number="Pending")
            db.session.add(profile)
            db.session.commit()
        else:
            db.session.add(user)
            db.session.commit()

        flash('Registered successfully! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# =========================================
# ADMIN ROUTES
# =========================================

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin': return redirect(url_for('login'))
    
    # --- ADD DOCTOR LOGIC (Handles the Popup Form) ---
    if request.method == 'POST':
        # Combine First and Last Name
        name = request.form.get('first_name') + " " + request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        pwd = request.form.get('password')
        license_num = request.form.get('license')
        dept = request.form.get('department')
        
        # Generate Username from Email (e.g. john@email.com -> john)
        username = email.split('@')[0]
        
        if not User.query.filter_by(username=username).first():
            # Create User
            new_doc = User(username=username, password=generate_password_hash(pwd), role='doctor', name=name, email=email, phone=phone)
            db.session.add(new_doc)
            db.session.commit()
            
            # Create Profile
            profile = DoctorProfile(user_id=new_doc.id, department=dept, license_number=license_num)
            db.session.add(profile)
            db.session.commit()
            
            flash('Doctor Added Successfully', 'success')
        else:
            flash('User already exists', 'danger')

    # --- SEARCH LOGIC ---
    search_query = request.args.get('search')
    dept_filter = request.args.get('department') # <--- Get the selected department

    # 1. Start with base queries
    doc_query = User.query.filter_by(role='doctor')
    pat_query = User.query.filter_by(role='patient')

    # 2. Apply Text Search (Name or Username)
    if search_query:
        doc_query = doc_query.filter(User.name.contains(search_query) | User.username.contains(search_query))
        pat_query = pat_query.filter(User.name.contains(search_query) | User.username.contains(search_query))

    # 3. Apply Department Filter (Specific to Doctors)
    if dept_filter and dept_filter != "":
        # Join with DoctorProfile table to check the department column
        doc_query = doc_query.join(DoctorProfile).filter(DoctorProfile.department == dept_filter)

    # 4. Execute Queries
    doctors = doc_query.all()
    patients = pat_query.all()

    # Stats
    stats = {
        'docs': User.query.filter_by(role='doctor').count(),
        'patients': User.query.filter_by(role='patient').count(),
        'appts': Appointment.query.count()
    }
    
    # Pass 'departments' keys for the dropdown
    return render_template('admin_dashboard.html', 
                           doctors=doctors, 
                           patients=patients, 
                           stats=stats,
                           departments=DEPT_DESCRIPTIONS.keys())

    

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin': return redirect(url_for('login'))
    user = User.query.get(id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        
        # Update Doctor Specifics
        if user.role == 'doctor':
            user.doctor_profile.department = request.form.get('department')
            user.doctor_profile.fee = request.form.get('fee')
            
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('edit_user.html', user=user)

@app.route('/admin/appointments')
@login_required
def admin_appointments():
    if current_user.role != 'admin': return redirect(url_for('login'))
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('admin_appointments.html', appointments=appointments)
@app.route('/admin/appointment_action/<int:id>/<action>')
@login_required
def admin_appointment_action(id, action):
    # Security check: ensure only admin can access this
    if current_user.role != 'admin': 
        return redirect(url_for('login'))
    
    appt = Appointment.query.get(id)
    if appt:
        if action == 'delete':
            db.session.delete(appt)
            flash('Appointment deleted permanently.', 'success')
        elif action == 'cancel':
            appt.status = 'Cancelled'
            flash('Appointment cancelled.', 'warning')
        
        db.session.commit()
    
    return redirect(url_for('admin_appointments'))

@app.route('/admin/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.role == 'admin':
        user = User.query.get(id)
        if user:
            if user.role == 'doctor':
                DoctorProfile.query.filter_by(user_id=id).delete()
                # Delete appointments assigned to this doctor to prevent errors
                Appointment.query.filter_by(doctor_id=id).delete()
            elif user.role == 'patient':
                # Delete patient's history
                Appointment.query.filter_by(patient_id=id).delete()
            
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_patient/<int:id>')
@login_required
def delete_patient(id):
    return delete_user(id)

@app.route('/admin/blacklist/<int:id>')
@login_required
def blacklist_user(id):
    if current_user.role == 'admin':
        user = User.query.get(id)
        user.is_active_user = not user.is_active_user
        db.session.commit()
        flash('User status updated', 'info')
    return redirect(url_for('admin_dashboard'))

# =========================================
# DOCTOR ROUTES
# =========================================

@app.route('/doctor', methods=['GET', 'POST'])
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor': return redirect(url_for('login'))
    
    # 1. Appointments
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.date.asc()).all()
    
    # 2. Patients (Unique)
    patient_ids = [a.patient_id for a in appointments]
    my_patients = User.query.filter(User.id.in_(list(set(patient_ids)))).all()

    # 3. Availability (Next 7 Days)
    today = datetime.now().date()
    next_7_days = []
    for i in range(7):
        day = today + timedelta(days=i)
        avail = Availability.query.filter_by(doctor_id=current_user.id, date=day).first()
        status = avail.is_available if avail else True # Default: Available
        next_7_days.append({'date': day, 'status': status})

    return render_template('doctor_dashboard.html', 
                         appointments=appointments, 
                         my_patients=my_patients,
                         next_7_days=next_7_days)

@app.route('/doctor/action/<int:id>/<action>')
@login_required
def appointment_action(id, action):
    appt = Appointment.query.get(id)
    if appt.doctor_id == current_user.id:
        if action == 'done': appt.status = 'Completed'
        if action == 'cancel': appt.status = 'Cancelled'
        db.session.commit()
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/complete_appointment/<int:id>', methods=['POST'])
@login_required
def complete_appointment(id):
    appt = Appointment.query.get(id)
    if appt.doctor_id == current_user.id:
        appt.diagnosis = request.form.get('diagnosis')
        appt.treatment = request.form.get('treatment')
        appt.prescription = request.form.get('prescription')
        appt.status = 'Completed'
        db.session.commit()
        flash('Treatment recorded successfully', 'success')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/cancel_appointment/<int:id>')
@login_required
def cancel_appointment_doc(id):
    appt = Appointment.query.get(id)
    if appt.doctor_id == current_user.id:
        appt.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled', 'info')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/toggle_availability/<string:date_str>')
@login_required
def toggle_availability(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    avail = Availability.query.filter_by(doctor_id=current_user.id, date=date_obj).first()
    
    if avail:
        avail.is_available = not avail.is_available
    else:
        new_avail = Availability(doctor_id=current_user.id, date=date_obj, is_available=False)
        db.session.add(new_avail)
    
    db.session.commit()
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/view_history/<int:patient_id>')
@login_required
def view_patient_history(patient_id):
    # This route can be used if you want a standalone page, 
    # but currently, we handle history via Modals in the dashboard.
    # Leaving it here in case you want to expand later.
    return redirect(url_for('doctor_dashboard'))

# =========================================
# PATIENT ROUTES
# =========================================

# ==========================================
# PASTE THIS INTO app.py (Replace existing patient_dashboard)
# ==========================================

@app.route('/patient', methods=['GET', 'POST'])
@login_required
def patient_dashboard():
    if current_user.role != 'patient': return redirect(url_for('login'))
    
    # 1. Departments (for the dropdown and list)
    departments = DEPT_DESCRIPTIONS.keys()
    
    # 2. Appointments Logic
    all_appts = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.date.desc()).all()
    upcoming_appts = [a for a in all_appts if a.status == 'Booked']
    history_appts = [a for a in all_appts if a.status in ['Completed', 'Cancelled']]

    # 3. SEARCH & FILTER LOGIC (NEW)
    search_query = request.args.get('search')
    dept_filter = request.args.get('department')

    # Start with base query for doctors
    doc_query = User.query.filter_by(role='doctor')

    # Apply Name Search
    if search_query:
        doc_query = doc_query.filter(User.name.contains(search_query))
    
    # Apply Department Filter
    if dept_filter and dept_filter != "All":
        doc_query = doc_query.join(DoctorProfile).filter(DoctorProfile.department == dept_filter)

    doctors = doc_query.all()

    # 4. Availability Logic (Calculated only for filtered doctors)
    today = datetime.now().date()
    doc_availability = {}
    
    for doc in doctors:
        week_avail = []
        for i in range(7):
            day = today + timedelta(days=i)
            avail_entry = Availability.query.filter_by(doctor_id=doc.id, date=day).first()
            is_open = avail_entry.is_available if avail_entry else True 
            week_avail.append({'date': day, 'status': is_open, 'day_name': day.strftime('%a')})
        doc_availability[doc.id] = week_avail
    if request.args.get('search') or request.args.get('department'):
        active_tab = 'doctors'
    else:
        active_tab = 'home'

    return render_template('patient_dashboard.html', 
                           departments=departments, 
                           upcoming_appts=upcoming_appts, 
                           history_appts=history_appts,
                           doctors=doctors,
                           doc_availability=doc_availability,
                           active_tab=active_tab)

@app.route('/patient/edit_profile', methods=['POST'])
@login_required
def edit_patient_profile():
    if current_user.role != 'patient': return redirect(url_for('login'))
    
    current_user.name = request.form.get('name')
    current_user.email = request.form.get('email')
    current_user.phone = request.form.get('phone')
    
    # Optional Password Change
    new_pwd = request.form.get('password')
    if new_pwd:
        current_user.password = generate_password_hash(new_pwd)
        
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('patient_dashboard'))

@app.route('/department/<string:dept_name>')
@login_required
def department_details(dept_name):
    doctors = User.query.join(DoctorProfile).filter(DoctorProfile.department == dept_name).all()
    description = DEPT_DESCRIPTIONS.get(dept_name, "Details not available.")
    
    # Get the specific image, or use a default one if not found
    dept_image = DEPT_IMAGES.get(dept_name, "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?q=80&w=2000&auto=format&fit=crop")
    
    return render_template('department_details.html', 
                           dept_name=dept_name, 
                           doctors=doctors, 
                           description=description, 
                           dept_image=dept_image)

@app.route('/book_page/<int:doc_id>', methods=['GET'])
@login_required
def book_page(doc_id):
    doctor = User.query.get(doc_id)
    return render_template('book_appointment.html', doctor=doctor)

@app.route('/book/<int:doc_id>', methods=['POST'])
@login_required
def book_appointment(doc_id):
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    symptoms = request.form.get('symptoms')
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        # Handle time HH:MM or HH:MM:SS
        if len(time_str) == 5:
             time_obj = datetime.strptime(time_str, '%H:%M').time()
        else:
             time_obj = datetime.strptime(time_str, '%H:%M:%S').time()

        new_appt = Appointment(patient_id=current_user.id, doctor_id=doc_id, date=date_obj, time=time_obj, symptoms=symptoms)
        db.session.add(new_appt)
        db.session.commit()
        flash('Appointment Booked', 'success')
    except Exception as e:
        flash(f'Error booking: {str(e)}', 'danger')
        
    return redirect(url_for('patient_dashboard'))

@app.route('/patient/cancel/<int:id>')
@login_required
def patient_cancel(id):
    appt = Appointment.query.get(id)
    if appt.patient_id == current_user.id:
        appt.status = 'Cancelled'
        db.session.commit()
    return redirect(url_for('patient_dashboard'))
@app.route('/reschedule_appointment/<int:id>', methods=['GET', 'POST'])
@login_required 
def reschedule_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    # Security check: Ensure the current user owns this appointment
    if appointment.patient_id != current_user.id:
        flash('You are not authorized to reschedule this appointment.', 'danger')
        return redirect(url_for('patient_dashboard'))

    if request.method == 'POST':
        new_date_str = request.form.get('new_date')
        
        # Convert string date from form to Python date object
        # (Adjust format '%Y-%m-%d' if your input is different)
        try:
            new_date = datetime.strptime(new_date_str, '%Y-%m-%d').date()
            
            # Update the appointment
            appointment.date = new_date
            appointment.status = 'Rescheduled' # Optional: Update status
            db.session.commit()
            
            flash('Appointment rescheduled successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
            
        except ValueError:
            flash('Invalid date format.', 'danger')

    return render_template('reschedule_appointment.html', appointment=appointment)

if __name__ == '__main__':
    app.run(debug=True)