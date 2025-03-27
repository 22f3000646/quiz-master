from flask import render_template,Flask,redirect,url_for,session,flash
from forms import *
from config import SECRET_KEY
from werkzeug.security import generate_password_hash,check_password_hash
app= Flask(__name__)
from flask_login import login_user,LoginManager,logout_user,login_required,current_user
from routes import user_blueprint
from admin import admin
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizmaster.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
from extension import db
from models import User,Student_details,create_database
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  
from flask_migrate import Migrate
migrate = Migrate(app,db)
app.register_blueprint(user_blueprint,url_prefix="/student")
app.register_blueprint(admin,url_prefix="/admin")
app.config['SECRET_KEY'] = SECRET_KEY
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  
        if current_user.role == "admin":  
            return redirect(url_for('admin.dashboard')) 
        return redirect(url_for('user_blueprint.dashboard'))  
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(Email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            if user.role=="admin":
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user_blueprint.dashboard'))
        else:
            flash("incorrect username or password !",'unsuccess')
            return render_template('login.html',form=form)
            
    return render_template('login.html',form=form)
@app.route('/registration',methods =["GET","POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_username = User.query.filter_by(Email = form.email.data).first()
        if existing_username:
            flash('Email already exists','error')
            return redirect(url_for('registration'))
        image = form.image.data
        name = form.first_name.data
        email = form.email.data
        phone = form.phone.data
        password = generate_password_hash(form.password.data) 
        dob = form.dob.data
        qualification = form.qualification.data
        new_user = User(Email = email,password = password , role ="student")
        db.session.add(new_user)
        db.session.flush()
        new_details = Student_details(u_id = new_user.id,full_name = name ,qualification = qualification , dob = dob , phone = phone,profile_picture_name = image.filename,profile_picture = image.read())
        db.session.add(new_details)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html',form = form)

@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__=="__main__":
    with app.app_context():
        with app.app_context():
            create_database()
    app.run(debug=True)