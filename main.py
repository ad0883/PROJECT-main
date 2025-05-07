from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'mayank'

# Login manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Email setup
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME="a.dwivedi@gmail.com",  # <-- Replace with your Gmail
    MAIL_PASSWORD="Password"             # <-- Replace with app-specific password
)
mail = Mail(app)

# SQLite database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hmdbms.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    usertype = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(1000))

class Patients(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    slot = db.Column(db.String(50))
    disease = db.Column(db.String(50))
    time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50))
    number = db.Column(db.String(50))

class Doctors(db.Model):
    did = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    doctorname = db.Column(db.String(50))
    dept = db.Column(db.String(50))

class Trigr(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    action = db.Column(db.String(50))
    timestamp = db.Column(db.String(50))

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def home():
    current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', current_datetime=current_datetime)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctors', methods=['POST', 'GET'])
def doctors():
    if request.method == "POST":
        email = request.form.get('email')
        doctorname = request.form.get('doctorname')
        dept = request.form.get('dept')
        doc = Doctors(email=email, doctorname=doctorname, dept=dept)
        db.session.add(doc)
        db.session.commit()
        flash("Information is Stored", "primary")
    return render_template('doctor.html')

@app.route('/patients', methods=['POST', 'GET'])
@login_required
def patient():
    doct = Doctors.query.all()
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        time = request.form.get('time')
        date = request.form.get('date')
        dept = request.form.get('dept')
        number = request.form.get('number')
        subject = "HOSPITAL MANAGEMENT SYSTEM"

        patient = Patients(email=email, name=name, gender=gender, slot=slot, disease=disease,
                           time=time, date=date, dept=dept, number=number)
        db.session.add(patient)
        db.session.commit()

        # Send mail
        try:
            mail.send_message(subject,
                              sender=app.config['MAIL_USERNAME'],
                              recipients=[email],
                              body=f"YOUR BOOKING IS CONFIRMED\nDetails:\nName: {name}\nSlot: {slot}")
        except Exception as e:
            flash(f"Email sending failed: {str(e)}", "danger")

        flash("Booking Confirmed", "info")

    return render_template('patient.html', doct=doct)

@app.route("/ask-ai")
def ask_ai():
    # Redirect to the Streamlit app running on localhost:8501
    return redirect("http://localhost:8501")

@app.route('/bookings')
@login_required
def bookings():
    em = current_user.email
    if current_user.usertype == "Doctor":
        query = Patients.query.all()
    else:
        query = Patients.query.filter_by(email=em).all()
    return render_template('booking.html', query=query)

@app.route("/edit/<string:pid>", methods=['POST', 'GET'])
@login_required
def edit(pid):
    posts = Patients.query.get(pid)
    if request.method == "POST":
        posts.email = request.form.get('email')
        posts.name = request.form.get('name')
        posts.gender = request.form.get('gender')
        posts.slot = request.form.get('slot')
        posts.disease = request.form.get('disease')
        posts.time = request.form.get('time')
        posts.date = request.form.get('date')
        posts.dept = request.form.get('dept')
        posts.number = request.form.get('number')
        db.session.commit()
        flash("Slot is Updated", "success")
        return redirect('/bookings')
    return render_template('edit.html', posts=posts)

@app.route("/delete/<string:pid>", methods=['POST', 'GET'])
@login_required
def delete(pid):
    patient = Patients.query.get(pid)
    db.session.delete(patient)
    db.session.commit()
    flash("Slot Deleted Successfully", "danger")
    return redirect('/bookings')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        usertype = request.form.get('usertype')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exists", "warning")
            return render_template('signup.html')
        encpassword = generate_password_hash(password)
        new_user = User(username=username, usertype=usertype, email=email, password=encpassword)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Successful. Please Login.", "success")
        return render_template('login.html')
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Explicitly clear the session
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except Exception as e:
        return f'Database connection failed: {e}'

@app.route('/details', methods=['GET', 'POST'])
@login_required
def details():
    if request.method == 'POST':
        pid = request.form.get('pid')
        department = request.form.get('department')

        patient = Patients.query.get(pid)
        if patient and not patient.dept:
            patient.dept = department
            db.session.commit()
            flash('Department updated successfully!', 'success')
        else:
            flash('Department already selected or invalid patient.', 'danger')

    patients = Patients.query.all()
    return render_template('details.html', patients=patients)

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == "POST":
        query = request.form.get('search')
        dept = Doctors.query.filter_by(dept=query).first()
        name = Doctors.query.filter_by(doctorname=query).first()
        if name or dept:
            flash("Doctor is Available", "info")
        else:
            flash("Doctor is Not Available", "danger")
    return render_template('index.html')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

if __name__ == '__main__':
    # Check if the SQLite database exists, if not create one
    with app.app_context():  # Set up application context
        db.create_all()      # Create all tables
    app.run(debug=True)