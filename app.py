import os
from dotenv import load_dotenv
load_dotenv()

# app.py (Fixed Flask Backend)
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import re
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from time import time
import logging
from threading import Thread
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import generate_password_hash



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - Move to environment variables in production
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'daveagidani@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'uhmnahncpwfxftcr')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alumni.db'
app.config['UPLOAD_FOLDER'] = 'static/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
USERS_PER_PAGE = 16  # Your requested 16 users per page

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    graduation_year = db.Column(db.String(10))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Utility Functions
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            logger.info("Email sent successfully")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, recipients, body, html_body=None):
    """Send email with error handling"""
    try:
        msg = Message(
            subject=subject,
            sender=app.config['MAIL_USERNAME'],
            recipients=recipients
        )
        msg.body = body
        if html_body:
            msg.html = html_body
        
        # Send asynchronously to avoid blocking
        thread = Thread(target=send_async_email, args=(app, msg))
        thread.start()
        return True
    except Exception as e:
        logger.error(f"Error preparing email: {str(e)}")
        return False

def require_login(f):
    """Decorator to require user login"""
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def require_admin(f):
    """Decorator to require admin privileges"""
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Context Processors
@app.context_processor
def inject_year():
    return {'current_year': datetime.utcnow().year}

@app.context_processor
def inject_user():
    user = None
    is_admin = False
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
        if user:
            is_admin = user.is_admin
    return dict(current_user=user, is_admin=is_admin)

# Routes
@app.route('/')
def home():
    user_id = session.get('user_id')
    if user_id and User.query.get(user_id):
        return redirect(url_for('dashboard'))
    return render_template('home.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname   = request.form.get('fullname')
        email      = request.form.get('email')
        password   = request.form.get('password')
        city       = request.form.get('city')
        country    = request.form.get('country')
        graduation_year = request.form.get('graduation_year')
        phone      = request.form.get('phone')      # ← NEW
        bio        = request.form.get('bio')        # ← NEW
        admin_code = request.form.get('admin_code')

        if User.query.filter_by(email=email).first():
            flash("That email is already registered. Please log in or use another address.", "warning")
            return redirect(url_for('register'))

        # Build location
        location = ", ".join(filter(None, [city, country]))

        # Determine admin
        is_admin = False
        if admin_code and admin_code == os.getenv('ADMIN_CODE'):
            is_admin = True

        # Handle picture upload
        pic_file = request.files.get('profile_pic')
        if pic_file and allowed_file(pic_file.filename):
            filename = secure_filename(pic_file.filename)
            upload_dir = os.path.join(app.root_path, 'static', 'profile_pics')
            os.makedirs(upload_dir, exist_ok=True)
            pic_file.save(os.path.join(upload_dir, filename))
            pic_name = filename
        else:
            pic_name = 'default.jpg'

        try:
            user = User(
                fullname=fullname,
                email=email,
                password_hash=generate_password_hash(password),
                graduation_year=graduation_year,
                location=location,
                phone=phone,                   # ← PASS IT IN
                bio=bio,                       # ← PASS IT IN
                profile_pic=pic_name,
                is_admin=is_admin
            )
            db.session.add(user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {e}")
            flash("Registration failed. Try again.", "danger")

    return render_template('register.html')
   

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user'] = user.email
            session['user_id'] = user.id
            logger.info(f"User logged in: {email}")
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@require_login
def dashboard():
    user = User.query.get(session['user_id'])
    recent_news = News.query.order_by(News.date_posted.desc()).limit(3).all()
    upcoming_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date).limit(3).all()
    return render_template('dashboard.html', user=user, recent_news=recent_news, upcoming_events=upcoming_events)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))
    

@app.route('/news')
@require_login
def news():
    try:
        page = request.args.get('page', 1, type=int)
        news_items = News.query.order_by(News.date_posted.desc()).paginate(
            page=page, per_page=10, error_out=False
        )
        return render_template('news.html', news=news_items)
    except Exception as e:
        logger.error(f'News page error: {str(e)}')
        flash('An error occurred loading news.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/dashboard')
@require_admin
def admin_dashboard():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'overview')  # Track which tab is active
    
    # Paginate users for the users tab
    users_paginated = User.query.order_by(User.created_at.desc()).paginate(
        page=page if tab == 'users' else 1,
        per_page=USERS_PER_PAGE,
        error_out=False
    )
    
    # Get all news and events (you can paginate these too if needed)
    news = News.query.order_by(News.date_posted.desc()).all()
    events = Event.query.order_by(Event.created_at.desc()).all()
    
    stats = {
        'total_users': User.query.count(),
        'total_news': News.query.count(),
        'total_events': Event.query.count(),
        'recent_registrations': User.query.filter(
            User.created_at >= datetime.now().replace(day=1)
        ).count()
    }
    
    return render_template('admin_dashboard.html', 
                         users=users_paginated, 
                         news=news, 
                         events=events, 
                         stats=stats,
                         active_tab=tab)

@app.route('/admin/create_event', methods=['GET', 'POST'])
@require_admin
def create_event():
    form = request.form  # make `form` available in template

    if request.method == 'POST':
        # pull and strip
        title       = form.get('title', '').strip()
        description = form.get('description', '').strip()
        date_str    = form.get('date', '').strip()

        # validate presence
        if not all([title, description, date_str]):
            flash('All fields are required.', 'error')
            return render_template('create_event.html', form=form)

        # parse date
        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format.', 'error')
            return render_template('create_event.html', form=form)

        try:
            # create & commit
            event = Event(
                title=title,
                description=description,
                date=event_date,
                author_id=session['user_id']
            )
            db.session.add(event)
            db.session.commit()

            # notify users
            try:
                users = User.query.all()
                emails = [u.email for u in users if u.email]
                batch_size = 50

                for i in range(0, len(emails), batch_size):
                    send_email(
                        subject=f'New Event: {title}',
                        recipients=emails[i:i+batch_size],
                        body=f"""
Hello Alumni,

A new event has been created:

Event: {title}
Date: {event_date.strftime('%B %d, %Y')}
Description: {description}

Best regards,
Baptist High School Makurdi Alumni Association
"""
                    )

                flash(f'Event created! Notifications sent to {len(emails)} alumni.', 'success')

            except Exception as notify_err:
                app.logger.error(f'Error sending notifications: {notify_err}')
                flash('Event created, but error sending notifications.', 'warning')

            return redirect(url_for('admin_dashboard'))

        except Exception as db_err:
            db.session.rollback()
            app.logger.error(f'Error creating event: {db_err}')
            flash('An error occurred while creating the event.', 'error')
            return render_template('create_event.html', form=form)

    # GET → just show the blank form
    return render_template('create_event.html', form=form)

@app.route('/admin/post_news', methods=['POST'])
@require_admin
def post_news():
    try:
        title = request.form.get('news_title', '').strip()
        content = request.form.get('news_content', '').strip()
        
        if not title or not content:
            flash('Both title and content are required.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        news = News(
            title=title,
            content=content,
            author_id=session['user_id']
        )
        
        db.session.add(news)
        db.session.commit()
        
        logger.info(f"News posted: {title}")
        flash('News posted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error posting news: {str(e)}')
        flash('An error occurred while posting news.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/promote_user/<int:user_id>', methods=['POST'])
@require_admin
def promote_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
            logger.info(f"User promoted to admin: {user.email}")
            flash(f'{user.fullname} has been promoted to admin.', 'success')
        else:
            flash('User is already an admin.', 'error')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error promoting user: {str(e)}')
        flash('An error occurred while promoting user.', 'error')
    
    # Redirect back to users tab with pagination
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('admin_dashboard', tab='users', page=page))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@require_admin
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        if user.id == session['user_id']:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin_dashboard'))
        
        db.session.delete(user)
        db.session.commit()
        logger.info(f"User deleted: {user.email}")
        flash('User deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting user: {str(e)}')
        flash('An error occurred while deleting user.', 'error')
    
    # Redirect back to users tab with pagination
    page = request.args.get('page', 1, type=int)
    return redirect(url_for('admin_dashboard', tab='users', page=page))

@app.route('/admin/delete_news/<int:news_id>', methods=['POST'])
@require_admin
def delete_news(news_id):
    try:
        news = News.query.get_or_404(news_id)
        db.session.delete(news)
        db.session.commit()
        flash('News deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting news: {str(e)}')
        flash('An error occurred while deleting news.', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_event/<int:event_id>', methods=['POST'])
@require_admin
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting event: {str(e)}')
        flash('An error occurred while deleting event.', 'error')
    
    return redirect(url_for('admin_dashboard'))



@app.route('/admin/manage_alumni')
@require_admin
def manage_alumni():
    # Add pagination to manage alumni page
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.fullname).paginate(
        page=page,
        per_page=USERS_PER_PAGE,
        error_out=False
    )
    return render_template('manage_alumni.html', users=users)

@app.route('/edit_profile', methods=['GET', 'POST'])
@require_login
def edit_profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            user.fullname = request.form.get('name', '').strip()
            user.graduation_year = request.form.get('graduation_year')
            user.bio = request.form.get('bio', '').strip()
            
            # Phone validation
            phone = request.form.get('phone', '').strip()
            if phone and (len(phone) != 10 or not phone.isdigit()):
                flash('Phone number must be 10 digits.', 'error')
                return render_template('edit_profile.html', user=user)
            
            if phone:
                user.phone = f'+234{phone}'
            
            # Location
            country = request.form.get('country', '').strip()
            city = request.form.get('city', '').strip()
            if country and city:
                user.location = f"{city}, {country}"
            
            # Profile picture
            profile_pic = request.files.get('profile_pic')
            if profile_pic and profile_pic.filename and allowed_file(profile_pic.filename):
                filename = f"{int(time())}_{secure_filename(profile_pic.filename)}"
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_pic = filename
            
            db.session.commit()
            logger.info(f"Profile updated: {user.email}")
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating profile: {str(e)}')
            flash('An error occurred while updating profile.', 'error')
    
    return render_template('edit_profile.html', user=user)

@app.route('/change_password', methods=['GET', 'POST'])
@require_login
def change_password():
    if request.method == 'POST':
        user = User.query.get(session['user_id'])
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        
        if not user.check_password(old_password):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        
        if not re.match(r'^(?=.*[A-Z])(?=.*\W).{8,}$', new_password):
            flash('Password must be at least 8 characters, include a capital letter and a symbol.', 'error')
            return render_template('change_password.html')
        
        try:
            user.set_password(new_password)
            db.session.commit()
            logger.info(f"Password changed: {user.email}")
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error changing password: {str(e)}')
            flash('An error occurred while changing password.', 'error')
    
    return render_template('change_password.html')

@app.route('/search', methods=['GET'])
@require_login
def search():
    # Get search parameters
    query = request.args.get('query', '').strip()
    graduation_year = request.args.get('graduation_year', '')
    location = request.args.get('location', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Build the query
    users_query = User.query
    
    if query:
        users_query = users_query.filter(User.fullname.ilike(f'%{query}%'))
    if graduation_year:
        users_query = users_query.filter_by(graduation_year=graduation_year)
    if location:
        users_query = users_query.filter(User.location.ilike(f'%{location}%'))
    
    # Paginate the results
    users = users_query.order_by(User.fullname).paginate(
        page=page,
        per_page=USERS_PER_PAGE,
        error_out=False
    )
    
    years = [str(year) for year in range(2014, 2026)]
    
    return render_template('search.html', 
                         users=users, 
                         query=query, 
                         graduation_year=graduation_year, 
                         location=location, 
                         years=years)

@app.route('/user/<int:user_id>')
@require_login
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)

@app.route('/donate')
@require_login
def donate():
    return render_template('donate.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Rate limiting
        now = time()
        last_sent = session.get('last_reset_sent', 0)
        if now - last_sent < 60:  # 1 minute cooldown
            remaining = int(60 - (now - last_sent))
            flash(f'Please wait {remaining} seconds before requesting another reset link.', 'error')
            return render_template('forgot_password.html')
        
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                token = generate_reset_token(email)
                reset_url = url_for('reset_password', token=token, _external=True)
                
                subject = 'Password Reset Request - Baptist High School Makurdi Alumni'
                body = f"""
Hello {user.fullname},

You have requested a password reset for your Alumni Portal account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this reset, please ignore this email.

Best regards,
Baptist High School Makurdi Alumni Association
                """
                
                if send_email(subject, [email], body):
                    session['last_reset_sent'] = now
                    flash('Password reset email sent! Check your inbox.', 'success')
                else:
                    flash('An error occurred sending the reset email.', 'error')
                    
            except Exception as e:
                logger.error(f'Error sending password reset: {str(e)}')
                flash('An error occurred. Please try again later.', 'error')
        else:
            # Don't reveal if email exists or not for security
            flash('If that email is registered, a reset link has been sent.', 'success')
    
    return render_template('forgot_password.html')
app.config['DEBUG'] = True  # Add this line temporarily
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid reset link.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        
        if not re.match(r'^(?=.*[A-Z])(?=.*\W).{8,}$', password):
            flash('Password must be at least 8 characters, include a capital letter and a symbol.', 'error')
            return render_template('reset_password.html')
        
        try:
            user.set_password(password)
            db.session.commit()
            logger.info(f"Password reset completed: {email}")
            flash('Password reset successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error resetting password: {str(e)}')
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('reset_password.html')


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# @app.errorhandler(500)
# def internal_error(error):
#     db.session.rollback()
#     logger.error(f'Server Error: {error}')
#     return render_template('500.html'), 500

# # Create tables and run app
# if __name__ == '__main__':
#     with app.app_context():
#         try:
#             db.create_all()
#             # Create upload directory
#             os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#             logger.info("Database and upload folder initialized")
#         except Exception as e:
#             logger.error(f"Initialization error: {str(e)}")




# Database initialization
try:
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully!")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")
        
except Exception as e:
    logger.error(f"Error creating database tables: {e}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
        