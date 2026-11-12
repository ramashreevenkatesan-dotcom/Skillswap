"""
SkillSwap — A Peer-to-Peer Skill Learning and Exchange Platform
Flask Application Backend
"""

import os
import re
import secrets
from datetime import datetime, timezone
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from models import (
    db, User, Skill, LearningInterest, ExchangeRequest, Session, Review,
    seed_database_if_empty
)

# Initialize Flask application
app = Flask(__name__, instance_relative_config=True)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'skillswap-production-grade-secret-key-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    f"sqlite:///{os.path.join(app.instance_path, 'skillswap.db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance directory exists
os.makedirs(app.instance_path, exist_ok=True)

# Initialize Database with App
db.init_app(app)

# Automatic database initialization on startup without deleting existing data
with app.app_context():
    db.create_all()
    seed_database_if_empty()


# ==========================================
# SECURITY & AUTHENTICATION UTILITIES
# ==========================================

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_csrf_token():
    token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
    expected = session.get('_csrf_token')
    if not expected or not token or not secrets.compare_digest(token, expected):
        return False
    return True

@app.context_processor
def inject_global_template_vars():
    user = None
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
    now_utc = datetime.now(timezone.utc)
    return {
        'current_user': user,
        'csrf_token': generate_csrf_token(),
        'now': now_utc,
        'current_year': now_utc.year
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.path))
        user = db.session.get(User, session['user_id'])
        if not user:
            session.clear()
            flash("Session expired. Please log in again.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[@$!%*?&#^_\-]', password):
        return False, "Password must contain at least one special character (@$!%*?&#^_-)."
    return True, ""


# ==========================================
# SKILL MATCHING ALGORITHM (RULE-BASED)
# ==========================================

def calculate_skill_matches(user):
    """
    Transparent, deterministic rule-based matching algorithm.
    Compares teaching skills, learning interests, learning mode, language, and availability.
    Categorizes matches as:
    1. Strong Reciprocal Match (User A teaches what User B wants AND User B teaches what User A wants)
    2. Partial Match (Direct Learning Opportunity or Mentorship Opportunity)
    """
    my_teach_skills = user.skills_taught.filter_by(status='active').all()
    my_interests = user.learning_interests.all()

    all_other_users = User.query.filter(User.id != user.id).all()
    matches = []

    for other in all_other_users:
        other_teach_skills = other.skills_taught.filter_by(status='active').all()
        other_interests = other.learning_interests.all()

        if not other_teach_skills and not other_interests:
            continue

        # Check Direction 1: Can I learn from other?
        matching_skills_to_learn = []
        for o_skill in other_teach_skills:
            o_title_lower = o_skill.title.lower()
            o_cat_lower = o_skill.category.lower()
            for my_int in my_interests:
                int_name_lower = my_int.skill_name.lower()
                int_cat_lower = (my_int.category or "").lower()
                if (int_name_lower in o_title_lower or 
                    o_title_lower in int_name_lower or 
                    (int_cat_lower and int_cat_lower == o_cat_lower)):
                    matching_skills_to_learn.append((o_skill, my_int))
                    break

        # Check Direction 2: Can other learn from me?
        matching_skills_to_teach = []
        for my_skill in my_teach_skills:
            my_title_lower = my_skill.title.lower()
            my_cat_lower = my_skill.category.lower()
            for o_int in other_interests:
                int_name_lower = o_int.skill_name.lower()
                int_cat_lower = (o_int.category or "").lower()
                if (int_name_lower in my_title_lower or 
                    my_title_lower in int_name_lower or 
                    (int_cat_lower and int_cat_lower == my_cat_lower)):
                    matching_skills_to_teach.append((my_skill, o_int))
                    break

        # Compatibility factors
        mode_match = (
            user.preferred_mode == other.preferred_mode or 
            user.preferred_mode == 'Hybrid' or 
            other.preferred_mode == 'Hybrid'
        )
        lang_match = (user.preferred_language.lower() == other.preferred_language.lower())

        if matching_skills_to_learn and matching_skills_to_teach:
            teach_pair = matching_skills_to_teach[0]
            learn_pair = matching_skills_to_learn[0]
            score = 95
            if mode_match: score += 3
            if lang_match: score += 2

            explanation = (
                f"Strong Reciprocal Match! You teach '{teach_pair[0].title}' which {other.full_name} "
                f"wants to learn, and {other.full_name} teaches '{learn_pair[0].title}' which aligns with "
                f"your learning goal for '{learn_pair[1].skill_name}'."
            )

            matches.append({
                'user': other,
                'match_type': 'Strong Reciprocal Match',
                'badge_class': 'badge-success',
                'score': score,
                'teach_skill': teach_pair[0],
                'learn_skill': learn_pair[0],
                'explanation': explanation,
                'other_teach_skills': other_teach_skills,
                'other_interests': other_interests,
                'mode_match': mode_match,
                'lang_match': lang_match
            })

        elif matching_skills_to_learn:
            learn_pair = matching_skills_to_learn[0]
            score = 70
            if mode_match: score += 3
            if lang_match: score += 2

            explanation = (
                f"Partial Match (Learning Opportunity): {other.full_name} offers '{learn_pair[0].title}', "
                f"matching your target interest in '{learn_pair[1].skill_name}'."
            )

            matches.append({
                'user': other,
                'match_type': 'Partial Match',
                'badge_class': 'badge-primary',
                'score': score,
                'teach_skill': my_teach_skills[0] if my_teach_skills else None,
                'learn_skill': learn_pair[0],
                'explanation': explanation,
                'other_teach_skills': other_teach_skills,
                'other_interests': other_interests,
                'mode_match': mode_match,
                'lang_match': lang_match
            })

        elif matching_skills_to_teach:
            teach_pair = matching_skills_to_teach[0]
            score = 65
            if mode_match: score += 3
            if lang_match: score += 2

            explanation = (
                f"Partial Match (Mentorship Opportunity): You teach '{teach_pair[0].title}', "
                f"which {other.full_name} is seeking to learn."
            )

            matches.append({
                'user': other,
                'match_type': 'Partial Match',
                'badge_class': 'badge-info',
                'score': score,
                'teach_skill': teach_pair[0],
                'learn_skill': other_teach_skills[0] if other_teach_skills else None,
                'explanation': explanation,
                'other_teach_skills': other_teach_skills,
                'other_interests': other_interests,
                'mode_match': mode_match,
                'lang_match': lang_match
            })

    # Sort descending by match score
    matches.sort(key=lambda m: m['score'], reverse=True)
    return matches


# ==========================================
# CORE ROUTES
# ==========================================

@app.route('/')
def index():
    """Landing Page"""
    categories = [
        {"name": "Programming", "icon": "code", "desc": "Python, Java, C++, Systems"},
        {"name": "Web Development", "icon": "globe", "desc": "HTML, CSS, JavaScript, APIs"},
        {"name": "App Development", "icon": "smartphone", "desc": "Flutter, React Native, iOS"},
        {"name": "UI/UX Design", "icon": "layout", "desc": "Figma, Wireframing, UX Design"},
        {"name": "Artificial Intelligence", "icon": "cpu", "desc": "Machine Learning, NLP, Data"},
        {"name": "Public Speaking", "icon": "mic", "desc": "Storytelling, Pitches, Debate"}
    ]
    # Featured real active skills from database
    featured_skills = Skill.query.filter_by(status='active').order_by(Skill.created_at.desc()).limit(6).all()
    return render_template('index.html', categories=categories, featured_skills=featured_skills)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Login Module"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if not validate_csrf_token():
            flash("Security token missing or invalid. Please try again.", "danger")
            return redirect(url_for('login'))

        email_or_username = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email_or_username or not password:
            flash("Please provide both email/username and password.", "danger")
            return render_template('login.html', email=email_or_username)

        # Authenticate against SQLite
        user = User.query.filter(
            (User.email == email_or_username.lower()) | (User.username == email_or_username)
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please verify your credentials.", "danger")
            return render_template('login.html', email=email_or_username)

        # Setup session
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['full_name'] = user.full_name

        flash(f"Welcome back, {user.full_name}!", "success")
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User Registration Module"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        if not validate_csrf_token():
            flash("Security token missing or invalid.", "danger")
            return redirect(url_for('signup'))

        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        institution = request.form.get('institution', '').strip() or 'Apex Institute of Technology'
        department = request.form.get('department', '').strip() or 'Computer Science'
        biography = request.form.get('biography', '').strip()
        teach_skills = request.form.get('teach_skills', '').strip()
        learn_skills = request.form.get('learn_skills', '').strip()
        preferred_mode = request.form.get('preferred_mode', 'Online')
        preferred_language = request.form.get('preferred_language', 'English')

        # Form validations
        if not full_name or not username or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template('signup.html', form=request.form)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash("Please enter a valid email address.", "danger")
            return render_template('signup.html', form=request.form)

        if len(username) < 3 or not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash("Username must be at least 3 characters and contain only letters, numbers, and underscores.", "danger")
            return render_template('signup.html', form=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('signup.html', form=request.form)

        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            flash(msg, "danger")
            return render_template('signup.html', form=request.form)

        # Unique checks
        if User.query.filter_by(username=username).first():
            flash("Username is already taken. Please choose another.", "danger")
            return render_template('signup.html', form=request.form)

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists. Please log in.", "danger")
            return render_template('signup.html', form=request.form)

        # Create user
        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            institution=institution,
            department=department,
            biography=biography or "College student excited to learn and share skills.",
            preferred_mode=preferred_mode,
            preferred_language=preferred_language
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Add initial teaching skill if provided
        if teach_skills:
            first_teach = teach_skills.split(',')[0].strip()
            if first_teach:
                s = Skill(
                    user_id=new_user.id,
                    title=first_teach,
                    category="Programming" if "code" in first_teach.lower() or "python" in first_teach.lower() else "General",
                    description=f"Peer session teaching {first_teach}. Hands-on practice and clear foundational concepts.",
                    experience_level="Intermediate",
                    teaching_language=preferred_language,
                    learning_mode=preferred_mode,
                    status="active"
                )
                db.session.add(s)

        # Add initial learning interests if provided
        if learn_skills:
            for item in [x.strip() for x in learn_skills.split(',') if x.strip()]:
                interest = LearningInterest(
                    user_id=new_user.id,
                    skill_name=item,
                    category="General"
                )
                db.session.add(interest)

        db.session.commit()
        flash("Registration successful! You can now log in with your credentials.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
def logout():
    """User Logout Module"""
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('index'))


# ==========================================
# DASHBOARD MODULE
# ==========================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard Module with Real Database Metrics and Activities"""
    user = db.session.get(User, session['user_id'])

    # Real database statistics
    skills_to_learn_count = Skill.query.filter(
        Skill.user_id != user.id,
        Skill.status == 'active'
    ).count()

    skills_offered_count = user.skills_taught.count()

    pending_requests_count = ExchangeRequest.query.filter(
        (ExchangeRequest.recipient_id == user.id) | (ExchangeRequest.sender_id == user.id),
        ExchangeRequest.status == 'pending'
    ).count()

    completed_exchanges_count = user.completed_exchanges_count

    # Recommended Skills from database (active, not own)
    # Prioritize skills that match user's learning interests
    user_interest_names = [i.skill_name.lower() for i in user.learning_interests.all()]
    all_other_skills = Skill.query.filter(
        Skill.user_id != user.id,
        Skill.status == 'active'
    ).order_by(Skill.created_at.desc()).all()

    recommended_skills = []
    # Match interests first
    for s in all_other_skills:
        if any(int_name in s.title.lower() or int_name in s.category.lower() for int_name in user_interest_names):
            recommended_skills.append(s)
    # Then fill remaining
    for s in all_other_skills:
        if s not in recommended_skills and len(recommended_skills) < 6:
            recommended_skills.append(s)

    # Recent activities (Requests, Sessions, Reviews)
    recent_requests = ExchangeRequest.query.filter(
        (ExchangeRequest.sender_id == user.id) | (ExchangeRequest.recipient_id == user.id)
    ).order_by(ExchangeRequest.updated_at.desc()).limit(5).all()

    # Active upcoming sessions
    user_req_ids = [r.id for r in ExchangeRequest.query.filter(
        (ExchangeRequest.sender_id == user.id) | (ExchangeRequest.recipient_id == user.id)
    ).all()]
    upcoming_sessions = Session.query.filter(
        Session.exchange_request_id.in_(user_req_ids),
        Session.status == 'scheduled'
    ).order_by(Session.scheduled_date.asc()).limit(3).all() if user_req_ids else []

    # Reciprocal Match quick count
    matches = calculate_skill_matches(user)
    reciprocal_count = sum(1 for m in matches if m['match_type'] == 'Strong Reciprocal Match')

    return render_template(
        'dashboard.html',
        user=user,
        skills_to_learn_count=skills_to_learn_count,
        skills_offered_count=skills_offered_count,
        pending_requests_count=pending_requests_count,
        completed_exchanges_count=completed_exchanges_count,
        recommended_skills=recommended_skills[:4],
        recent_requests=recent_requests,
        upcoming_sessions=upcoming_sessions,
        reciprocal_count=reciprocal_count
    )


# ==========================================
# LEARN MODULE
# ==========================================

@app.route('/learn')
def learn():
    """Explore Skills to Learn with Real DB Filtering & Search"""
    query = Skill.query.filter_by(status='active')

    # Exclude user's own skills if logged in
    current_uid = session.get('user_id')
    if current_uid:
        query = query.filter(Skill.user_id != current_uid)

    # Filter parameters
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    level = request.args.get('level', '').strip()
    mode = request.args.get('mode', '').strip()
    language = request.args.get('language', '').strip()
    sort = request.args.get('sort', 'newest')

    if search:
        query = query.join(User, Skill.user_id == User.id).filter(
            (Skill.title.ilike(f"%{search}%")) |
            (Skill.description.ilike(f"%{search}%")) |
            (Skill.category.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    if category and category != 'All':
        query = query.filter(Skill.category == category)

    if level and level != 'All':
        query = query.filter(Skill.experience_level == level)

    if mode and mode != 'All':
        query = query.filter(Skill.learning_mode == mode)

    if language and language != 'All':
        query = query.filter(Skill.teaching_language == language)

    if sort == 'newest':
        query = query.order_by(Skill.created_at.desc())
    elif sort == 'oldest':
        query = query.order_by(Skill.created_at.asc())
    elif sort == 'title':
        query = query.order_by(Skill.title.asc())

    skills = query.all()

    categories = [
        "All", "Programming", "Web Development", "App Development", 
        "Data Science", "Artificial Intelligence", "UI/UX Design", 
        "Graphic Design", "Video Editing", "Communication", 
        "Public Speaking", "Languages", "Mathematics", "Business", "Other"
    ]

    return render_template(
        'learn.html',
        skills=skills,
        categories=categories,
        current_search=search,
        current_category=category,
        current_level=level,
        current_mode=mode,
        current_language=language,
        current_sort=sort,
        total_count=len(skills)
    )


# ==========================================
# SKILL DETAILS PAGE
# ==========================================

@app.route('/skill/<int:skill_id>')
def skill_details(skill_id):
    """Detailed View of a Single Skill"""
    skill = db.session.get(Skill, skill_id)
    if not skill:
        abort(404)

    is_owner = (session.get('user_id') == skill.user_id)
    reviews = []
    # Fetch reviews associated with this skill
    reqs = ExchangeRequest.query.filter_by(learn_skill_id=skill.id, status='completed').all()
    if reqs:
        reviews = Review.query.filter(Review.exchange_request_id.in_([r.id for r in reqs])).all()

    # Related skills in same category
    related_skills = Skill.query.filter(
        Skill.category == skill.category,
        Skill.id != skill.id,
        Skill.status == 'active'
    ).limit(3).all()

    return render_template(
        'skill_details.html',
        skill=skill,
        is_owner=is_owner,
        reviews=reviews,
        related_skills=related_skills
    )


# ==========================================
# TEACH MODULE
# ==========================================

@app.route('/teach', methods=['GET', 'POST'])
@login_required
def teach():
    """Teach Module: View, Add, and Manage Teaching Listings"""
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        if not validate_csrf_token():
            flash("Security token invalid.", "danger")
            return redirect(url_for('teach'))

        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        experience_level = request.form.get('experience_level', 'Intermediate')
        teaching_language = request.form.get('teaching_language', 'English').strip()
        learning_mode = request.form.get('learning_mode', 'Online')
        session_duration = request.form.get('session_duration', '45-60 mins').strip()
        available_days = request.form.get('available_days', '').strip()
        available_times = request.form.get('available_times', '').strip()
        resources = request.form.get('resources', '').strip()
        outcomes = request.form.get('outcomes', '').strip()

        # Validation
        if not title or not category or not description:
            flash("Skill title, category, and description are required.", "danger")
            return redirect(url_for('teach'))

        new_skill = Skill(
            user_id=user.id,
            title=title,
            category=category,
            description=description,
            experience_level=experience_level,
            teaching_language=teaching_language,
            learning_mode=learning_mode,
            session_duration=session_duration,
            available_days=available_days or "Weekdays",
            available_times=available_times or "Flexible",
            resources=resources or "Custom curated materials and templates",
            outcomes=outcomes or "Skill proficiency and practical mastery",
            status='active'
        )
        db.session.add(new_skill)
        db.session.commit()

        flash(f"'{title}' has been successfully published to the Learn catalog!", "success")
        return redirect(url_for('teach'))

    my_skills = user.skills_taught.order_by(Skill.created_at.desc()).all()
    categories = [
        "Programming", "Web Development", "App Development", 
        "Data Science", "Artificial Intelligence", "UI/UX Design", 
        "Graphic Design", "Video Editing", "Communication", 
        "Public Speaking", "Languages", "Mathematics", "Business", "Other"
    ]

    return render_template('teach.html', user=user, my_skills=my_skills, categories=categories)


@app.route('/teach/<int:skill_id>/edit', methods=['POST'])
@login_required
def edit_skill(skill_id):
    """Edit an existing skill (Owner-Only)"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('teach'))

    skill = db.session.get(Skill, skill_id)
    if not skill or skill.user_id != session['user_id']:
        flash("You are not authorized to edit this listing.", "danger")
        return redirect(url_for('teach'))

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()

    if not title or not category or not description:
        flash("Title, category, and description are required.", "danger")
        return redirect(url_for('teach'))

    skill.title = title
    skill.category = category
    skill.description = description
    skill.experience_level = request.form.get('experience_level', skill.experience_level)
    skill.teaching_language = request.form.get('teaching_language', skill.teaching_language)
    skill.learning_mode = request.form.get('learning_mode', skill.learning_mode)
    skill.session_duration = request.form.get('session_duration', skill.session_duration)
    skill.available_days = request.form.get('available_days', skill.available_days)
    skill.available_times = request.form.get('available_times', skill.available_times)
    skill.resources = request.form.get('resources', skill.resources)
    skill.outcomes = request.form.get('outcomes', skill.outcomes)

    db.session.commit()
    flash(f"Skill '{skill.title}' updated successfully.", "success")
    return redirect(url_for('teach'))


@app.route('/teach/<int:skill_id>/toggle-status', methods=['POST'])
@login_required
def toggle_skill_status(skill_id):
    """Pause or Reactivate a skill listing"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('teach'))

    skill = db.session.get(Skill, skill_id)
    if not skill or skill.user_id != session['user_id']:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('teach'))

    skill.status = 'paused' if skill.status == 'active' else 'active'
    db.session.commit()

    flash(f"Listing '{skill.title}' is now {skill.status}.", "info")
    return redirect(url_for('teach'))


@app.route('/teach/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    """Delete a skill listing (Owner-Only)"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('teach'))

    skill = db.session.get(Skill, skill_id)
    if not skill or skill.user_id != session['user_id']:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('teach'))

    title = skill.title
    db.session.delete(skill)
    db.session.commit()

    flash(f"Listing '{title}' deleted permanently.", "info")
    return redirect(url_for('teach'))


# ==========================================
# SKILL EXCHANGE MODULE & MATCHING
# ==========================================

@app.route('/skill-exchange')
@login_required
def skill_exchange():
    """Skill Exchange Matching Module with Transparent Algorithm"""
    user = db.session.get(User, session['user_id'])
    matches = calculate_skill_matches(user)
    my_teach_skills = user.skills_taught.filter_by(status='active').all()

    return render_template(
        'skill_exchange.html',
        user=user,
        matches=matches,
        my_teach_skills=my_teach_skills
    )


# ==========================================
# REQUESTS: LEARN REQUEST & PROPOSE EXCHANGE
# ==========================================

@app.route('/request-to-learn', methods=['POST'])
@login_required
def request_to_learn():
    """Submit a 1-way Learning Request from Learn or Skill Details page"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('learn'))

    user_id = session['user_id']
    skill_id = request.form.get('skill_id', type=int)
    message = request.form.get('message', '').strip()
    preferred_days = request.form.get('preferred_days', 'Flexible').strip()
    preferred_time = request.form.get('preferred_time', 'Flexible').strip()
    learning_mode = request.form.get('learning_mode', 'Online').strip()

    skill = db.session.get(Skill, skill_id)
    if not skill:
        flash("Selected skill was not found.", "danger")
        return redirect(url_for('learn'))

    # Security rule: Cannot request own skill
    if skill.user_id == user_id:
        flash("You cannot send a learning request for your own skill listing.", "warning")
        return redirect(url_for('skill_details', skill_id=skill.id))

    if not message:
        flash("Please explain your learning goals or what you hope to achieve.", "danger")
        return redirect(url_for('skill_details', skill_id=skill.id))

    # Prevent duplicate pending request
    existing = ExchangeRequest.query.filter_by(
        sender_id=user_id,
        recipient_id=skill.user_id,
        learn_skill_id=skill.id,
        status='pending'
    ).first()

    if existing:
        flash("You already have a pending learning request for this skill.", "info")
        return redirect(url_for('requests_page'))

    req = ExchangeRequest(
        sender_id=user_id,
        recipient_id=skill.user_id,
        request_type='learn',
        teach_skill_id=None,
        learn_skill_id=skill.id,
        message=message,
        preferred_days=preferred_days,
        preferred_time=preferred_time,
        learning_mode=learning_mode,
        status='pending'
    )
    db.session.add(req)
    db.session.commit()

    flash(f"Learning request sent to {skill.teacher.full_name}! Track it below.", "success")
    return redirect(url_for('requests_page'))


@app.route('/propose-exchange', methods=['POST'])
@login_required
def propose_exchange():
    """Submit a Reciprocal Skill Exchange Proposal"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('skill_exchange'))

    user_id = session['user_id']
    recipient_id = request.form.get('recipient_id', type=int)
    teach_skill_id = request.form.get('teach_skill_id', type=int)
    learn_skill_id = request.form.get('learn_skill_id', type=int)
    message = request.form.get('message', '').strip()
    preferred_days = request.form.get('preferred_days', 'Flexible').strip()
    preferred_time = request.form.get('preferred_time', 'Flexible').strip()
    learning_mode = request.form.get('learning_mode', 'Online').strip()

    if user_id == recipient_id:
        flash("You cannot propose an exchange to yourself.", "warning")
        return redirect(url_for('skill_exchange'))

    recipient = db.session.get(User, recipient_id)
    if not recipient:
        flash("Recipient student not found.", "danger")
        return redirect(url_for('skill_exchange'))

    # Validation: teach_skill must belong to sender
    teach_skill = db.session.get(Skill, teach_skill_id)
    if not teach_skill or teach_skill.user_id != user_id:
        flash("You must select a skill you actively teach.", "danger")
        return redirect(url_for('skill_exchange'))

    # Validation: learn_skill must belong to recipient
    learn_skill = db.session.get(Skill, learn_skill_id)
    if not learn_skill or learn_skill.user_id != recipient_id:
        flash("The requested learning skill must belong to the recipient.", "danger")
        return redirect(url_for('skill_exchange'))

    if not message:
        flash("Please provide an introduction message for your proposal.", "danger")
        return redirect(url_for('skill_exchange'))

    # Prevent duplicate active proposal
    existing = ExchangeRequest.query.filter_by(
        sender_id=user_id,
        recipient_id=recipient_id,
        teach_skill_id=teach_skill.id,
        learn_skill_id=learn_skill.id,
        status='pending'
    ).first()

    if existing:
        flash("An active proposal for these skills is already pending.", "info")
        return redirect(url_for('requests_page'))

    proposal = ExchangeRequest(
        sender_id=user_id,
        recipient_id=recipient_id,
        request_type='exchange',
        teach_skill_id=teach_skill.id,
        learn_skill_id=learn_skill.id,
        message=message,
        preferred_days=preferred_days,
        preferred_time=preferred_time,
        learning_mode=learning_mode,
        status='pending'
    )
    db.session.add(proposal)
    db.session.commit()

    flash(f"Exchange proposal successfully sent to {recipient.full_name}!", "success")
    return redirect(url_for('requests_page'))


# ==========================================
# REQUEST MANAGEMENT MODULE
# ==========================================

@app.route('/requests')
@login_required
def requests_page():
    """Request Management Module with Filtering Tabs"""
    user_id = session['user_id']
    tab = request.args.get('tab', 'all')

    base_query = ExchangeRequest.query.filter(
        (ExchangeRequest.sender_id == user_id) | (ExchangeRequest.recipient_id == user_id)
    )

    if tab == 'sent':
        reqs = base_query.filter(ExchangeRequest.sender_id == user_id).order_by(ExchangeRequest.created_at.desc()).all()
    elif tab == 'received':
        reqs = base_query.filter(ExchangeRequest.recipient_id == user_id).order_by(ExchangeRequest.created_at.desc()).all()
    elif tab == 'learning':
        reqs = base_query.filter(ExchangeRequest.request_type == 'learn').order_by(ExchangeRequest.created_at.desc()).all()
    elif tab == 'exchanges':
        reqs = base_query.filter(ExchangeRequest.request_type == 'exchange').order_by(ExchangeRequest.created_at.desc()).all()
    elif tab in ('pending', 'accepted', 'rejected', 'cancelled', 'completed'):
        reqs = base_query.filter(ExchangeRequest.status == tab).order_by(ExchangeRequest.updated_at.desc()).all()
    else:
        reqs = base_query.order_by(ExchangeRequest.updated_at.desc()).all()

    # Precalculate counts for tab badges
    counts = {
        'all': base_query.count(),
        'sent': base_query.filter(ExchangeRequest.sender_id == user_id).count(),
        'received': base_query.filter(ExchangeRequest.recipient_id == user_id).count(),
        'pending': base_query.filter(ExchangeRequest.status == 'pending').count(),
        'accepted': base_query.filter(ExchangeRequest.status == 'accepted').count(),
        'completed': base_query.filter(ExchangeRequest.status == 'completed').count(),
        'rejected': base_query.filter(ExchangeRequest.status == 'rejected').count(),
        'cancelled': base_query.filter(ExchangeRequest.status == 'cancelled').count()
    }

    return render_template('requests.html', requests=reqs, current_tab=tab, counts=counts)


@app.route('/request/<int:request_id>')
@login_required
def request_details(request_id):
    """Detailed View of Single Request with History, Sessions, and Reviews"""
    user_id = session['user_id']
    req = db.session.get(ExchangeRequest, request_id)
    if not req:
        abort(404)

    # Authorization Check: Only participants can view
    if req.sender_id != user_id and req.recipient_id != user_id:
        flash("You are not authorized to view this request.", "danger")
        return redirect(url_for('requests_page'))

    sessions = req.sessions.order_by(Session.created_at.desc()).all()
    reviews = req.reviews.order_by(Review.created_at.desc()).all()

    # Check if current user already reviewed this exchange
    user_already_reviewed = any(r.reviewer_id == user_id for r in reviews)

    return render_template(
        'request_details.html',
        req=req,
        sessions=sessions,
        reviews=reviews,
        user_already_reviewed=user_already_reviewed
    )


@app.route('/request/<int:request_id>/status', methods=['POST'])
@login_required
def update_request_status(request_id):
    """Update status of a request: accept, reject, cancel, complete"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('requests_page'))

    user_id = session['user_id']
    new_status = request.form.get('status', '').strip().lower()

    req = db.session.get(ExchangeRequest, request_id)
    if not req:
        abort(404)

    # Authorization & Transition check
    if not req.can_transition_to(new_status, user_id):
        flash(f"Invalid operation or unauthorized to set status to '{new_status}'.", "danger")
        return redirect(url_for('request_details', request_id=req.id))

    req.status = new_status
    req.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    flash(f"Request #{req.id} has been marked as '{new_status}'.", "success")
    return redirect(url_for('request_details', request_id=req.id))


@app.route('/request/<int:request_id>/schedule-session', methods=['POST'])
@login_required
def schedule_session(request_id):
    """Schedule a learning session for an accepted request"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('requests_page'))

    user_id = session['user_id']
    req = db.session.get(ExchangeRequest, request_id)
    if not req or (req.sender_id != user_id and req.recipient_id != user_id):
        flash("Unauthorized.", "danger")
        return redirect(url_for('requests_page'))

    if req.status != 'accepted':
        flash("Sessions can only be scheduled for accepted requests.", "warning")
        return redirect(url_for('request_details', request_id=req.id))

    scheduled_date = request.form.get('scheduled_date', '').strip()
    scheduled_time = request.form.get('scheduled_time', '').strip()
    duration = request.form.get('duration', '60 mins').strip()
    meeting_mode = request.form.get('meeting_mode', 'Online').strip()
    meeting_link = request.form.get('meeting_link', '').strip() or 'https://meet.jit.si/skillswap-peer'
    notes = request.form.get('notes', '').strip()

    if not scheduled_date or not scheduled_time:
        flash("Please provide both session date and time.", "danger")
        return redirect(url_for('request_details', request_id=req.id))

    sess = Session(
        exchange_request_id=req.id,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        duration=duration,
        meeting_mode=meeting_mode,
        meeting_link=meeting_link,
        notes=notes or "Cover core concepts and practical implementation."
    )
    db.session.add(sess)
    db.session.commit()

    flash("Learning session scheduled successfully!", "success")
    return redirect(url_for('request_details', request_id=req.id))


@app.route('/request/<int:request_id>/review', methods=['POST'])
@login_required
def submit_review(request_id):
    """Submit a peer review for a completed exchange"""
    if not validate_csrf_token():
        flash("Security token invalid.", "danger")
        return redirect(url_for('requests_page'))

    user_id = session['user_id']
    req = db.session.get(ExchangeRequest, request_id)
    if not req or (req.sender_id != user_id and req.recipient_id != user_id):
        flash("Unauthorized.", "danger")
        return redirect(url_for('requests_page'))

    if req.status != 'completed':
        flash("Reviews can only be submitted after the exchange has been marked completed.", "warning")
        return redirect(url_for('request_details', request_id=req.id))

    # The user being reviewed is the other participant
    reviewed_user_id = req.recipient_id if user_id == req.sender_id else req.sender_id

    # Check if already reviewed
    existing = Review.query.filter_by(
        exchange_request_id=req.id,
        reviewer_id=user_id
    ).first()

    if existing:
        flash("You have already submitted a review for this exchange.", "info")
        return redirect(url_for('request_details', request_id=req.id))

    rating = request.form.get('rating', type=int)
    comment = request.form.get('comment', '').strip()

    if not rating or rating < 1 or rating > 5:
        flash("Please select a rating between 1 and 5 stars.", "danger")
        return redirect(url_for('request_details', request_id=req.id))

    if not comment:
        flash("Please write a helpful review comment.", "danger")
        return redirect(url_for('request_details', request_id=req.id))

    rev = Review(
        exchange_request_id=req.id,
        reviewer_id=user_id,
        reviewed_user_id=reviewed_user_id,
        rating=rating,
        comment=comment
    )
    db.session.add(rev)
    db.session.commit()

    flash("Your review has been published to the student's profile!", "success")
    return redirect(url_for('request_details', request_id=req.id))


# ==========================================
# USER PROFILE & EDIT PROFILE MODULES
# ==========================================

@app.route('/profile')
@login_required
def profile():
    """Current User Profile"""
    user = db.session.get(User, session['user_id'])
    return show_user_profile(user, is_self=True)


@app.route('/profile/<username>')
def public_profile(username):
    """View Any User Profile"""
    user = User.query.filter_by(username=username).first_or_404()
    is_self = (session.get('user_id') == user.id)
    return show_user_profile(user, is_self=is_self)


def show_user_profile(user, is_self=False):
    skills = user.skills_taught.order_by(Skill.created_at.desc()).all()
    interests = user.learning_interests.all()
    reviews = user.reviews_received.order_by(Review.created_at.desc()).all()

    # Pre-fetch user skills if logged in to facilitate exchange proposal modal
    current_user_skills = []
    if 'user_id' in session and not is_self:
        c_user = db.session.get(User, session['user_id'])
        current_user_skills = c_user.skills_taught.filter_by(status='active').all()

    return render_template(
        'profile.html',
        profile_user=user,
        is_self=is_self,
        skills=skills,
        interests=interests,
        reviews=reviews,
        current_user_skills=current_user_skills
    )


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit Profile Module (Self-Only)"""
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        if not validate_csrf_token():
            flash("Security token invalid.", "danger")
            return redirect(url_for('edit_profile'))

        full_name = request.form.get('full_name', '').strip()
        institution = request.form.get('institution', '').strip()
        department = request.form.get('department', '').strip()
        biography = request.form.get('biography', '').strip()
        preferred_mode = request.form.get('preferred_mode', 'Online')
        preferred_language = request.form.get('preferred_language', 'English')
        availability_days = request.form.get('availability_days', '').strip()
        availability_times = request.form.get('availability_times', '').strip()
        profile_image = request.form.get('profile_image', 'avatar_default')
        raw_interests = request.form.get('learning_interests', '').strip()

        if not full_name:
            flash("Full name cannot be empty.", "danger")
            return redirect(url_for('edit_profile'))

        user.full_name = full_name
        user.institution = institution or user.institution
        user.department = department or user.department
        user.biography = biography or user.biography
        user.preferred_mode = preferred_mode
        user.preferred_language = preferred_language
        user.availability_days = availability_days or user.availability_days
        user.availability_times = availability_times or user.availability_times
        user.profile_image = profile_image

        # Update learning interests
        LearningInterest.query.filter_by(user_id=user.id).delete()
        if raw_interests:
            for item in [x.strip() for x in raw_interests.split(',') if x.strip()]:
                db.session.add(LearningInterest(user_id=user.id, skill_name=item))

        db.session.commit()
        session['full_name'] = user.full_name

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    interests_str = ", ".join([i.skill_name for i in user.learning_interests.all()])
    return render_template('edit_profile.html', user=user, interests_str=interests_str)


# ==========================================
# SYSTEM WORKFLOW MODULE
# ==========================================

@app.route('/workflow')
def workflow():
    """System Workflow Module with 7 Visual Interactive Stages"""
    return render_template('workflow.html')


# ==========================================
# SETTINGS MODULE
# ==========================================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Settings Module: Password change, preferences, privacy"""
    user = db.session.get(User, session['user_id'])

    if request.method == 'POST':
        if not validate_csrf_token():
            flash("Security token invalid.", "danger")
            return redirect(url_for('settings'))

        action = request.form.get('action')

        if action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_new_pass = request.form.get('confirm_new_password', '')

            if not user.check_password(current_pass):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for('settings'))

            if new_pass != confirm_new_pass:
                flash("New passwords do not match.", "danger")
                return redirect(url_for('settings'))

            is_valid, msg = validate_password_strength(new_pass)
            if not is_valid:
                flash(msg, "danger")
                return redirect(url_for('settings'))

            user.set_password(new_pass)
            db.session.commit()
            flash("Password updated successfully!", "success")
            return redirect(url_for('settings'))

        elif action == 'update_preferences':
            user.preferred_mode = request.form.get('preferred_mode', user.preferred_mode)
            user.preferred_language = request.form.get('preferred_language', user.preferred_language)
            user.notify_email = bool(request.form.get('notify_email'))
            user.notify_requests = bool(request.form.get('notify_requests'))
            user.profile_visibility = request.form.get('profile_visibility', user.profile_visibility)

            db.session.commit()
            flash("Preferences saved successfully.", "success")
            return redirect(url_for('settings'))

    return render_template('settings.html', user=user)


# ==========================================
# APPLICATION ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', error_msg="The requested page could not be found."), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('index.html', error_msg="A server error occurred. Please try again."), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
