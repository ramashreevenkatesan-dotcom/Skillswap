from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(150), default='University Campus')
    department = db.Column(db.String(100), default='Computer Science')
    biography = db.Column(db.Text, default='Passionate learner and peer mentor.')
    profile_image = db.Column(db.String(255), default='avatar_default')
    preferred_mode = db.Column(db.String(50), default='Online')  # Online, In-Person, Hybrid
    preferred_language = db.Column(db.String(50), default='English')
    availability_days = db.Column(db.String(100), default='Monday, Wednesday, Friday')
    availability_times = db.Column(db.String(100), default='Evening (5 PM - 8 PM)')
    notify_email = db.Column(db.Boolean, default=True)
    notify_requests = db.Column(db.Boolean, default=True)
    profile_visibility = db.Column(db.String(20), default='public')
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships
    skills_taught = db.relationship('Skill', backref='teacher', cascade="all, delete-orphan", foreign_keys='Skill.user_id', lazy='dynamic')
    learning_interests = db.relationship('LearningInterest', backref='user', cascade="all, delete-orphan", lazy='dynamic')
    
    sent_requests = db.relationship('ExchangeRequest', backref='sender', foreign_keys='ExchangeRequest.sender_id', lazy='dynamic')
    received_requests = db.relationship('ExchangeRequest', backref='recipient', foreign_keys='ExchangeRequest.recipient_id', lazy='dynamic')
    
    reviews_given = db.relationship('Review', backref='reviewer', foreign_keys='Review.reviewer_id', lazy='dynamic')
    reviews_received = db.relationship('Review', backref='reviewed_user', foreign_keys='Review.reviewed_user_id', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        elif len(parts) == 1 and len(parts[0]) > 0:
            return parts[0][:2].upper()
        return "SS"

    @property
    def average_rating(self):
        reviews = list(self.reviews_received)
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def review_count(self):
        return self.reviews_received.count()

    @property
    def completed_exchanges_count(self):
        sent_completed = ExchangeRequest.query.filter_by(sender_id=self.id, status='completed').count()
        received_completed = ExchangeRequest.query.filter_by(recipient_id=self.id, status='completed').count()
        return sent_completed + received_completed

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'username': self.username,
            'email': self.email,
            'institution': self.institution,
            'department': self.department,
            'biography': self.biography,
            'preferred_mode': self.preferred_mode,
            'preferred_language': self.preferred_language,
            'average_rating': self.average_rating,
            'review_count': self.review_count,
            'completed_exchanges': self.completed_exchanges_count,
            'initials': self.initials,
            'created_at': self.created_at.strftime('%b %Y')
        }


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    experience_level = db.Column(db.String(50), nullable=False, default='Intermediate')  # Beginner, Intermediate, Advanced, Expert
    teaching_language = db.Column(db.String(50), default='English')
    learning_mode = db.Column(db.String(50), default='Online')  # Online, In-Person, Hybrid
    session_duration = db.Column(db.String(50), default='45-60 mins')
    available_days = db.Column(db.String(120), default='Weekdays')
    available_times = db.Column(db.String(120), default='Evenings')
    resources = db.Column(db.Text, default='Course notes, code templates, practice exercises')
    outcomes = db.Column(db.Text, default='Build a portfolio project and gain conceptual mastery')
    status = db.Column(db.String(20), default='active', index=True)  # active, paused
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Relationships for requests referring to this skill
    requests_as_teach = db.relationship('ExchangeRequest', backref='teach_skill', foreign_keys='ExchangeRequest.teach_skill_id', lazy='dynamic')
    requests_as_learn = db.relationship('ExchangeRequest', backref='learn_skill', foreign_keys='ExchangeRequest.learn_skill_id', lazy='dynamic')

    @property
    def rating_summary(self):
        # Calculate rating from reviews of completed requests for this skill
        req_ids = [r.id for r in ExchangeRequest.query.filter_by(learn_skill_id=self.id, status='completed').all()]
        if not req_ids:
            return self.teacher.average_rating
        skill_reviews = Review.query.filter(Review.exchange_request_id.in_(req_ids)).all()
        if not skill_reviews:
            return self.teacher.average_rating
        return round(sum(r.rating for r in skill_reviews) / len(skill_reviews), 1)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'experience_level': self.experience_level,
            'teaching_language': self.teaching_language,
            'learning_mode': self.learning_mode,
            'session_duration': self.session_duration,
            'available_days': self.available_days,
            'available_times': self.available_times,
            'resources': self.resources,
            'outcomes': self.outcomes,
            'status': self.status,
            'created_at': self.created_at.strftime('%b %d, %Y'),
            'teacher': {
                'id': self.teacher.id,
                'name': self.teacher.full_name,
                'username': self.teacher.username,
                'institution': self.teacher.institution,
                'department': self.teacher.department,
                'rating': self.teacher.average_rating,
                'initials': self.teacher.initials
            }
        }


class LearningInterest(db.Model):
    __tablename__ = 'learning_interests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(60), nullable=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'category': self.category
        }


class ExchangeRequest(db.Model):
    __tablename__ = 'exchange_requests'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    request_type = db.Column(db.String(20), nullable=False)  # 'learn' or 'exchange'
    teach_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=True)  # skill offered by sender (for reciprocal exchange)
    learn_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)  # skill requested from recipient
    message = db.Column(db.Text, nullable=False)
    preferred_days = db.Column(db.String(100), default='Weekdays')
    preferred_time = db.Column(db.String(100), default='Evenings')
    learning_mode = db.Column(db.String(50), default='Online')
    status = db.Column(db.String(20), default='pending', index=True)  # pending, accepted, rejected, cancelled, completed
    created_at = db.Column(db.DateTime, default=get_utc_now)
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    sessions = db.relationship('Session', backref='exchange_request', cascade="all, delete-orphan", lazy='dynamic')
    reviews = db.relationship('Review', backref='exchange_request', cascade="all, delete-orphan", lazy='dynamic')

    def can_transition_to(self, new_status, current_user_id):
        """
        Validate state machine transitions and permissions:
        - pending -> accepted (recipient only)
        - pending -> rejected (recipient only)
        - pending -> cancelled (sender only)
        - accepted -> cancelled (sender or recipient)
        - accepted -> completed (sender or recipient)
        """
        if self.status == 'pending':
            if new_status in ('accepted', 'rejected'):
                return self.recipient_id == current_user_id
            elif new_status == 'cancelled':
                return self.sender_id == current_user_id
        elif self.status == 'accepted':
            if new_status in ('cancelled', 'completed'):
                return current_user_id in (self.sender_id, self.recipient_id)
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'request_type': self.request_type,
            'sender': self.sender.to_dict(),
            'recipient': self.recipient.to_dict(),
            'learn_skill': self.learn_skill.to_dict() if self.learn_skill else None,
            'teach_skill': self.teach_skill.to_dict() if self.teach_skill else None,
            'message': self.message,
            'preferred_days': self.preferred_days,
            'preferred_time': self.preferred_time,
            'learning_mode': self.learning_mode,
            'status': self.status,
            'created_at': self.created_at.strftime('%b %d, %Y %I:%M %p'),
            'updated_at': self.updated_at.strftime('%b %d, %Y %I:%M %p'),
            'session_count': self.sessions.count(),
            'review_count': self.reviews.count()
        }


class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    exchange_request_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id'), nullable=False, index=True)
    scheduled_date = db.Column(db.String(50), nullable=False)
    scheduled_time = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), default='60 mins')
    meeting_mode = db.Column(db.String(50), default='Online (Google Meet / Zoom)')
    meeting_link = db.Column(db.String(255), default='https://meet.jit.si/skillswap-peer-session')
    notes = db.Column(db.Text, default='Review foundational concepts and code exercises together.')
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'exchange_request_id': self.exchange_request_id,
            'scheduled_date': self.scheduled_date,
            'scheduled_time': self.scheduled_time,
            'duration': self.duration,
            'meeting_mode': self.meeting_mode,
            'meeting_link': self.meeting_link,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.strftime('%b %d, %Y')
        }


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    exchange_request_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        return {
            'id': self.id,
            'exchange_request_id': self.exchange_request_id,
            'reviewer': {
                'id': self.reviewer.id,
                'name': self.reviewer.full_name,
                'username': self.reviewer.username,
                'initials': self.reviewer.initials
            },
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%b %d, %Y')
        }


def seed_database_if_empty():
    """
    Seeds initial realistic university peer records if User table is empty.
    Preserves all existing data if database already contains records.
    Never overwrites or deletes existing data.
    """
    if User.query.first() is not None:
        return  # Existing database preserved

    print("[SkillSwap] Empty database detected. Populating with initial peer records...")

    # Realistic student users
    u1 = User(
        full_name="Alex Morgan",
        username="alex_morgan",
        email="alex.morgan@campus.edu",
        institution="Apex Institute of Technology",
        department="Computer Science & Engineering",
        biography="3rd-year CS student passionate about full-stack web development and scalable backends. Looking to master UI/UX design and data visualization.",
        preferred_mode="Online",
        preferred_language="English",
        availability_days="Monday, Wednesday, Friday",
        availability_times="6:00 PM - 8:30 PM",
        created_at=datetime(2026, 1, 15, 10, 30)
    )
    u1.set_password("Password123!")

    u2 = User(
        full_name="Sarah Chen",
        username="sarah_chen",
        email="sarah.chen@campus.edu",
        institution="Apex Institute of Technology",
        department="Design & Human-Computer Interaction",
        biography="Senior Design major specializing in Figma design systems, design thinking, and interactive prototypes. Eager to learn Python backend and API architecture.",
        preferred_mode="Online",
        preferred_language="English",
        availability_days="Tuesday, Thursday, Saturday",
        availability_times="5:00 PM - 7:30 PM",
        created_at=datetime(2026, 1, 16, 11, 0)
    )
    u2.set_password("Password123!")

    u3 = User(
        full_name="Marcus Vance",
        username="marcus_vance",
        email="marcus.vance@campus.edu",
        institution="Metropolitan University",
        department="Data Science & AI",
        biography="Master's student working on machine learning pipelines, NLP, and PyTorch. Interested in learning mobile development (Flutter) and public speaking.",
        preferred_mode="Hybrid",
        preferred_language="English",
        availability_days="Weekends (Saturday & Sunday)",
        availability_times="10:00 AM - 1:00 PM",
        created_at=datetime(2026, 1, 18, 9, 15)
    )
    u3.set_password("Password123!")

    u4 = User(
        full_name="Priya Patel",
        username="priya_patel",
        email="priya.patel@campus.edu",
        institution="Apex Institute of Technology",
        department="Information Systems",
        biography="App developer with 2+ years building cross-platform Flutter and iOS apps. Excited to learn machine learning models and data analysis.",
        preferred_mode="Online",
        preferred_language="English",
        availability_days="Monday, Thursday",
        availability_times="7:00 PM - 9:00 PM",
        created_at=datetime(2026, 1, 20, 14, 0)
    )
    u4.set_password("Password123!")

    u5 = User(
        full_name="Liam Rodriguez",
        username="liam_rodriguez",
        email="liam.rodriguez@campus.edu",
        institution="State Technical College",
        department="Media & Communications",
        biography="Debate club president and digital storytelling mentor. Coaching students in confident presentation and pitch deck delivery. Learning web design.",
        preferred_mode="Hybrid",
        preferred_language="English",
        availability_days="Wednesday, Friday",
        availability_times="4:00 PM - 6:30 PM",
        created_at=datetime(2026, 1, 22, 16, 45)
    )
    u5.set_password("Password123!")

    db.session.add_all([u1, u2, u3, u4, u5])
    db.session.commit()

    # Learning Interests
    interests = [
        # Alex wants UI/UX Design and Public Speaking
        LearningInterest(user_id=u1.id, skill_name="UI/UX Design", category="UI/UX Design"),
        LearningInterest(user_id=u1.id, skill_name="Public Speaking", category="Public Speaking"),
        # Sarah wants Python and Web Development
        LearningInterest(user_id=u2.id, skill_name="Python Backend", category="Programming"),
        LearningInterest(user_id=u2.id, skill_name="Web Development", category="Web Development"),
        # Marcus wants App Development (Flutter) and Public Speaking
        LearningInterest(user_id=u3.id, skill_name="App Development", category="App Development"),
        LearningInterest(user_id=u3.id, skill_name="Public Speaking", category="Communication"),
        # Priya wants Artificial Intelligence and Data Science
        LearningInterest(user_id=u4.id, skill_name="Artificial Intelligence", category="Artificial Intelligence"),
        LearningInterest(user_id=u4.id, skill_name="Data Science", category="Data Science"),
        # Liam wants Web Development and Graphic Design
        LearningInterest(user_id=u5.id, skill_name="Web Development", category="Web Development"),
        LearningInterest(user_id=u5.id, skill_name="Graphic Design", category="Graphic Design"),
    ]
    db.session.add_all(interests)
    db.session.commit()

    # Skills Taught
    s1 = Skill(
        user_id=u1.id,
        title="Modern Python & Flask RESTful API Development",
        category="Programming",
        description="Comprehensive hands-on peer sessions covering Python 3, object-oriented concepts, Flask microframework, SQLAlchemy ORM, authentication tokens, and building secure REST APIs.",
        experience_level="Advanced",
        teaching_language="English",
        learning_mode="Online",
        session_duration="60 mins",
        available_days="Monday, Wednesday, Friday",
        available_times="6:00 PM - 8:30 PM",
        resources="GitHub repository templates, Postman collections, architectural cheatsheets",
        outcomes="Construct a production-ready REST API with SQLite/Postgres and user authentication",
        status="active"
    )

    s2 = Skill(
        user_id=u1.id,
        title="Responsive Frontend Architecture with Vanilla CSS & JS",
        category="Web Development",
        description="Master clean modern DOM manipulation, Flexbox, CSS Grid layouts, glassmorphism aesthetics, responsive viewports, and asynchronous Fetch API without heavy bloated dependencies.",
        experience_level="Intermediate",
        teaching_language="English",
        learning_mode="Online",
        session_duration="45-60 mins",
        available_days="Wednesday, Friday",
        available_times="7:00 PM - 9:00 PM",
        resources="Live CodeSandbox demos, CSS layout guides, UI component library",
        outcomes="Design and code completely custom, responsive web interfaces from scratch",
        status="active"
    )

    s3 = Skill(
        user_id=u2.id,
        title="Figma Design Systems & Interactive UI/UX Prototyping",
        category="UI/UX Design",
        description="Learn how to turn wireframes into high-fidelity design systems. We cover auto-layout, component variants, accessible typography, color tokens, and micro-interaction prototypes in Figma.",
        experience_level="Advanced",
        teaching_language="English",
        learning_mode="Online",
        session_duration="60 mins",
        available_days="Tuesday, Thursday, Saturday",
        available_times="5:00 PM - 7:30 PM",
        resources="Figma community kit, accessibility checklist, interactive UI playground",
        outcomes="Deliver an end-to-end Figma prototype ready for student developer handoff",
        status="active"
    )

    s4 = Skill(
        user_id=u3.id,
        title="Applied Machine Learning & Natural Language Processing",
        category="Artificial Intelligence",
        description="A practical dive into scikit-learn, Pandas, Hugging Face transformers, and text classification models. Perfect for university lab projects and capstone research.",
        experience_level="Expert",
        teaching_language="English",
        learning_mode="Hybrid",
        session_duration="60-75 mins",
        available_days="Weekends (Saturday & Sunday)",
        available_times="10:00 AM - 1:00 PM",
        resources="Jupyter notebooks, curated Kaggle datasets, model evaluation checklists",
        outcomes="Train, fine-tune, and evaluate an ML/NLP classification pipeline",
        status="active"
    )

    s5 = Skill(
        user_id=u4.id,
        title="Cross-Platform Mobile App Development with Flutter",
        category="App Development",
        description="Learn Dart fundamentals, widget tree hierarchy, state management (Provider / Bloc), API integration, and compiling natively for both iOS and Android simulator.",
        experience_level="Advanced",
        teaching_language="English",
        learning_mode="Online",
        session_duration="60 mins",
        available_days="Monday, Thursday",
        available_times="7:00 PM - 9:00 PM",
        resources="Sample Flutter starter codebase, UI widget gallery, API integration guides",
        outcomes="Publish a multi-screen mobile app with live network data fetching",
        status="active"
    )

    s6 = Skill(
        user_id=u5.id,
        title="Dynamic Public Speaking & Presentation Pitching",
        category="Public Speaking",
        description="Overcome presentation anxiety, structure compelling storytelling hooks, master vocal inflection, and deliver memorable technical and startup pitches for class or competitions.",
        experience_level="Advanced",
        teaching_language="English",
        learning_mode="Hybrid",
        session_duration="45 mins",
        available_days="Wednesday, Friday",
        available_times="4:00 PM - 6:30 PM",
        resources="Pitch deck template, speech outline frameworks, recorded rehearsal critiques",
        outcomes="Deliver a 5-minute technical presentation with high confidence and impact",
        status="active"
    )

    db.session.add_all([s1, s2, s3, s4, s5, s6])
    db.session.commit()

    # Completed Exchange between Alex and Sarah (Reciprocal Exchange)
    # Alex taught Sarah Python API (s1); Sarah taught Alex Figma UI/UX (s3)
    ex1 = ExchangeRequest(
        sender_id=u1.id,
        recipient_id=u2.id,
        request_type="exchange",
        teach_skill_id=s1.id,
        learn_skill_id=s3.id,
        message="Hi Sarah! I saw your Figma workshop listing and would love to learn UI/UX design systems. In return, I can help you build your Flask backend API for your portfolio project!",
        preferred_days="Tuesdays & Thursdays",
        preferred_time="6:00 PM",
        learning_mode="Online",
        status="completed",
        created_at=datetime(2026, 1, 25, 14, 0),
        updated_at=datetime(2026, 2, 10, 18, 0)
    )
    db.session.add(ex1)
    db.session.commit()

    # Sessions for ex1
    sess1 = Session(
        exchange_request_id=ex1.id,
        scheduled_date="2026-02-02",
        scheduled_time="6:00 PM",
        duration="60 mins",
        meeting_mode="Online (Google Meet)",
        meeting_link="https://meet.jit.si/skillswap-alex-sarah-session1",
        notes="Session 1: Figma Auto-Layout & Component Variants intro.",
        status="completed"
    )
    sess2 = Session(
        exchange_request_id=ex1.id,
        scheduled_date="2026-02-06",
        scheduled_time="6:00 PM",
        duration="60 mins",
        meeting_mode="Online (Google Meet)",
        meeting_link="https://meet.jit.si/skillswap-alex-sarah-session2",
        notes="Session 2: Flask REST API routing, SQLAlchemy models & JSON responses.",
        status="completed"
    )
    db.session.add_all([sess1, sess2])

    # Reviews for ex1
    rev1 = Review(
        exchange_request_id=ex1.id,
        reviewer_id=u1.id,
        reviewed_user_id=u2.id,
        rating=5,
        comment="Sarah is an exceptional mentor! She broke down complex Figma auto-layout principles into simple, intuitive mental models. My portfolio UI improved 10x.",
        created_at=datetime(2026, 2, 10, 19, 0)
    )
    rev2 = Review(
        exchange_request_id=ex1.id,
        reviewer_id=u2.id,
        reviewed_user_id=u1.id,
        rating=5,
        comment="Alex was patient, clear, and structured. In just two sessions, I had a working Flask backend connected to my design mockup. Best peer learning experience ever!",
        created_at=datetime(2026, 2, 10, 19, 30)
    )
    db.session.add_all([rev1, rev2])

    # Active Pending request from Marcus to Alex
    ex2 = ExchangeRequest(
        sender_id=u3.id,
        recipient_id=u1.id,
        request_type="learn",
        teach_skill_id=None,
        learn_skill_id=s2.id,
        message="Hey Alex, I really need help building a clean dashboard interface for my AI NLP project. Looking forward to learning CSS Grid and DOM handling from you!",
        preferred_days="Wednesday, Friday",
        preferred_time="7:00 PM",
        learning_mode="Online",
        status="pending",
        created_at=datetime(2026, 2, 20, 15, 30),
        updated_at=datetime(2026, 2, 20, 15, 30)
    )
    db.session.add(ex2)

    db.session.commit()
    print("[SkillSwap] Database populated successfully with 5 verified peer users, skills, and exchange history.")
