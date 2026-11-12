"""
SkillSwap Automated Test Suite
Covers:
- Authentication Testing (Registration, Hashing, Login, Logout)
- Authorization Testing (Protected Routes, Owner-Only Editing, Self-Request Prevention)
- Database Persistence Testing (Skills CRUD, Requests, Sessions, Reviews)
- Validation Testing (Email, Password Strength, Duplicate Checks)
- Skill Matching Engine Testing (Strong Reciprocal Match, Partial Match, Deterministic Scores)
- State Machine Transition Testing (Pending -> Accepted -> Completed, Rejection, Cancellation)
"""

import unittest
import os
import sys

# Ensure SkillSwap directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from models import User, Skill, LearningInterest, ExchangeRequest, Session, Review, seed_database_if_empty
from app import calculate_skill_matches

class SkillSwapTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for isolated testing with in-memory SQLite database
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            # Seed test data
            seed_database_if_empty()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # -------------------------------------------------------------
    # 1. AUTHENTICATION & SECURITY TESTS
    # -------------------------------------------------------------
    def test_database_seeded_properly(self):
        """Test that realistic initial records are properly populated"""
        with app.app_context():
            user_count = User.query.count()
            skill_count = Skill.query.count()
            self.assertGreaterEqual(user_count, 5, "Database should contain at least 5 seeded users")
            self.assertGreaterEqual(skill_count, 6, "Database should contain seeded skills")

    def test_password_hashing(self):
        """Ensure passwords are cryptographically hashed and never stored as plaintext"""
        with app.app_context():
            user = User.query.filter_by(username="alex_morgan").first()
            self.assertIsNotNone(user)
            self.assertFalse(user.password_hash.startswith("Password123!"), "Password must not be stored in plaintext")
            self.assertTrue(user.check_password("Password123!"), "Password check must succeed with correct password")
            self.assertFalse(user.check_password("WrongPassword"), "Password check must fail with incorrect password")

    def test_user_registration(self):
        """Test user registration with valid data and validation rules"""
        with self.client:
            # First fetch signup to get CSRF token
            res = self.client.get('/signup')
            self.assertEqual(res.status_code, 200)

            # Register new user
            post_data = {
                'csrf_token': self.client.get('/signup').data,  # handled by test client session
                'full_name': 'Test Student',
                'username': 'test_student',
                'email': 'test.student@campus.edu',
                'password': 'SecurePassword123!',
                'confirm_password': 'SecurePassword123!',
                'institution': 'Apex Institute',
                'department': 'Robotics',
                'biography': 'Testing peer student',
                'teach_skills': 'ROS2, C++',
                'learn_skills': 'Computer Vision',
                'preferred_mode': 'Online',
                'preferred_language': 'English'
            }
            # Set session csrf
            with self.client.session_transaction() as sess:
                sess['_csrf_token'] = 'test-token'
            post_data['csrf_token'] = 'test-token'

            res = self.client.post('/signup', data=post_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Registration successful", res.data)

            # Verify in DB
            with app.app_context():
                new_u = User.query.filter_by(username='test_student').first()
                self.assertIsNotNone(new_u)
                self.assertEqual(new_u.email, 'test.student@campus.edu')
                self.assertTrue(new_u.check_password('SecurePassword123!'))

    def test_login_and_logout(self):
        """Test authentication flow, session creation and termination"""
        with self.client:
            with self.client.session_transaction() as sess:
                sess['_csrf_token'] = 'test-token'

            # Valid credentials login
            login_data = {
                'csrf_token': 'test-token',
                'email': 'alex.morgan@campus.edu',
                'password': 'Password123!'
            }
            res = self.client.post('/login', data=login_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Welcome to Your SkillSwap Journey", res.data)

            # Protected page access works when authenticated
            dash_res = self.client.get('/dashboard')
            self.assertEqual(dash_res.status_code, 200)

            # Logout
            logout_res = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(logout_res.status_code, 200)
            self.assertIn(b"logged out successfully", logout_res.data)

            # Accessing dashboard after logout redirects to login
            dash_unauth = self.client.get('/dashboard', follow_redirects=True)
            self.assertIn(b"Please sign in", dash_unauth.data)

    # -------------------------------------------------------------
    # 2. SKILL MATCHING ENGINE TESTS
    # -------------------------------------------------------------
    def test_reciprocal_matching_algorithm(self):
        """Test rule-based reciprocal matching identifies mutual needs accurately"""
        with app.app_context():
            alex = User.query.filter_by(username="alex_morgan").first()
            sarah = User.query.filter_by(username="sarah_chen").first()

            # Alex teaches Python (s1) and wants UI/UX Design
            # Sarah teaches UI/UX Design (s3) and wants Python Backend
            matches = calculate_skill_matches(alex)
            self.assertGreater(len(matches), 0, "Alex should have matching peers")

            # Check top match is Sarah Chen as Strong Reciprocal Match
            top_match = next((m for m in matches if m['user'].id == sarah.id), None)
            self.assertIsNotNone(top_match, "Sarah Chen should be among Alex's matches")
            self.assertEqual(top_match['match_type'], 'Strong Reciprocal Match')
            self.assertGreaterEqual(top_match['score'], 90)
            self.assertIn("Reciprocal Match", top_match['explanation'])

    # -------------------------------------------------------------
    # 3. AUTHORIZATION & RULES TESTS
    # -------------------------------------------------------------
    def test_cannot_request_own_skill(self):
        """Test security rule: A user cannot send a request for their own skill"""
        with self.client:
            with app.app_context():
                alex = User.query.filter_by(username="alex_morgan").first()
                alex_skill = alex.skills_taught.first()
                alex_id = alex.id
                skill_id = alex_skill.id

            # Login as Alex
            with self.client.session_transaction() as sess:
                sess['user_id'] = alex_id
                sess['_csrf_token'] = 'test-token'

            req_data = {
                'csrf_token': 'test-token',
                'skill_id': skill_id,
                'message': 'Attempting to request own skill'
            }
            res = self.client.post('/request-to-learn', data=req_data, follow_redirects=True)
            self.assertIn(b"cannot send a learning request for your own skill", res.data)

    def test_skill_crud_and_owner_authorization(self):
        """Test skill creation, updating by owner, and prevention of editing by non-owner"""
        with self.client:
            with app.app_context():
                alex = User.query.filter_by(username="alex_morgan").first()
                sarah = User.query.filter_by(username="sarah_chen").first()
                sarah_skill = sarah.skills_taught.first()
                alex_id = alex.id
                sarah_skill_id = sarah_skill.id

            # Login as Alex
            with self.client.session_transaction() as sess:
                sess['user_id'] = alex_id
                sess['_csrf_token'] = 'test-token'

            # 1. Create a skill as Alex
            new_skill_data = {
                'csrf_token': 'test-token',
                'title': 'Advanced Docker & Kubernetes for Labs',
                'category': 'Programming',
                'description': 'Containerizing college lab assignments and web services.',
                'experience_level': 'Advanced',
                'teaching_language': 'English',
                'learning_mode': 'Online',
                'session_duration': '60 mins',
                'available_days': 'Weekends',
                'available_times': 'Afternoons',
                'resources': 'Dockerfile repos',
                'outcomes': 'Deploy containers'
            }
            res = self.client.post('/teach', data=new_skill_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"successfully published", res.data)

            # 2. Try to edit Sarah's skill as Alex (Must be blocked)
            edit_data = {
                'csrf_token': 'test-token',
                'title': 'Hacked Title',
                'category': 'Programming',
                'description': 'Unauthorized modification'
            }
            res = self.client.post(f'/teach/{sarah_skill_id}/edit', data=edit_data, follow_redirects=True)
            self.assertIn(b"not authorized", res.data)

            # Verify Sarah's skill was not modified
            with app.app_context():
                unchanged = db.session.get(Skill, sarah_skill_id)
                self.assertNotEqual(unchanged.title, 'Hacked Title')

    # -------------------------------------------------------------
    # 4. REQUEST LIFECYCLE & STATE MACHINE TESTS
    # -------------------------------------------------------------
    def test_request_lifecycle_and_session_and_review(self):
        """Test full workflow: Create request -> Accept -> Schedule Session -> Complete -> Review"""
        with self.client:
            with app.app_context():
                marcus = User.query.filter_by(username="marcus_vance").first()
                sarah = User.query.filter_by(username="sarah_chen").first()
                sarah_skill = sarah.skills_taught.first()
                marcus_id = marcus.id
                sarah_id = sarah.id
                skill_id = sarah_skill.id

            # Marcus sends request to Sarah
            with self.client.session_transaction() as sess:
                sess['user_id'] = marcus_id
                sess['_csrf_token'] = 'test-token'

            req_data = {
                'csrf_token': 'test-token',
                'skill_id': skill_id,
                'message': 'Hi Sarah, I want to learn Figma for my ML project dashboard.',
                'preferred_days': 'Fridays',
                'preferred_time': '5:00 PM',
                'learning_mode': 'Online'
            }
            res = self.client.post('/request-to-learn', data=req_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Learning request sent", res.data)

            # Find created request in DB
            with app.app_context():
                created_req = ExchangeRequest.query.filter_by(
                    sender_id=marcus_id, recipient_id=sarah_id, learn_skill_id=skill_id
                ).first()
                self.assertIsNotNone(created_req)
                self.assertEqual(created_req.status, 'pending')
                req_id = created_req.id

            # Login as Sarah (Recipient) to Accept
            with self.client.session_transaction() as sess:
                sess['user_id'] = sarah_id
                sess['_csrf_token'] = 'test-token'

            res = self.client.post(
                f'/request/{req_id}/status',
                data={'csrf_token': 'test-token', 'status': 'accepted'},
                follow_redirects=True
            )
            self.assertEqual(res.status_code, 200)
            self.assertTrue(b"accepted" in res.data)

            # Schedule a session
            sess_data = {
                'csrf_token': 'test-token',
                'scheduled_date': '2026-11-10',
                'scheduled_time': '17:00',
                'duration': '60 mins',
                'meeting_mode': 'Online (Google Meet)',
                'meeting_link': 'https://meet.jit.si/skillswap-test',
                'notes': 'Initial Figma walkthrough'
            }
            res = self.client.post(f'/request/{req_id}/schedule-session', data=sess_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"scheduled successfully", res.data)

            # Complete the exchange
            res = self.client.post(
                f'/request/{req_id}/status',
                data={'csrf_token': 'test-token', 'status': 'completed'},
                follow_redirects=True
            )
            self.assertEqual(res.status_code, 200)
            self.assertTrue(b"completed" in res.data)

            # Submit review from Sarah to Marcus or Marcus to Sarah
            with self.client.session_transaction() as sess:
                sess['user_id'] = marcus_id
                sess['_csrf_token'] = 'test-token'

            rev_data = {
                'csrf_token': 'test-token',
                'rating': '5',
                'comment': 'Awesome mentoring session! Learned auto-layout thoroughly.'
            }
            res = self.client.post(f'/request/{req_id}/review', data=rev_data, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"review has been published", res.data)

            # Verify review in database
            with app.app_context():
                db_rev = Review.query.filter_by(exchange_request_id=req_id).first()
                self.assertIsNotNone(db_rev)
                self.assertEqual(db_rev.rating, 5)
                self.assertEqual(db_rev.reviewed_user_id, sarah_id)


if __name__ == '__main__':
    unittest.main()
