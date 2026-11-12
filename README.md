# SkillSwap — Learn Together, Grow Together

**A Peer-to-Peer Student Skill Learning and Exchange Platform**

SkillSwap is a full-stack, responsive web application engineered for college students to teach skills they know, acquire skills they need from fellow peers, find reciprocal exchange partners, coordinate 1-on-1 learning sessions, and accumulate authentic peer ratings without monetary barriers.

Developed as a **College Design Studio Lab Project**, SkillSwap prioritizes authentic working functionality, database persistence via SQLite and SQLAlchemy, cryptographic password hashing, strict authorization and state machine transitions, and a transparent, deterministic skill matching engine.

---

## Key Highlights & Features

1. **Futuristic Student-Friendly Aesthetic**:
   - Modern Dark Glassmorphism interface styled in Deep Navy (`#0A0E1A`), Near Black, Purple (`#7000FF`), Electric Blue (`#3B82F6`), and Cyan Highlights (`#00F2FE`).
   - Custom SVG branding symbolizing orbital peer knowledge exchange.
   - Fully responsive on mobile, tablet, and desktop viewports.

2. **Real Database Records & Auto-Initialization**:
   - Automated SQLite database creation (`instance/skillswap.db`) on application startup.
   - Initialized with realistic university students (Computer Science, Design, AI, Mobile Dev, Communications), active skill listings across diverse academic disciplines, and verified peer review histories.
   - **Never deletes or overwrites** existing records on server restart.

3. **Transparent Rule-Based Matching Engine**:
   - Bilateral compatibility cross-referencing between a student's teaching capabilities and learning wishlist.
   - Differentiates between **Strong Reciprocal Matches** (User A teaches what User B wants *AND* User B teaches what User A wants) and **Partial Matches**.
   - Computes deterministic compatibility scores considering learning modes (Online, In-Person, Hybrid) and language preferences.
   - Zero black-box pseudo-AI claims; 100% transparent algorithmic explanations.

4. **Robust Security & Authorization**:
   - Cryptographic password hashing (`scrypt` / `pbkdf2:sha256` via Werkzeug).
   - Session-based authentication with protected route decorators (`@login_required`).
   - Anti-CSRF protection across all state-changing `POST` requests.
   - Strict ownership controls: Users can only edit/delete their own listings, cannot send requests for their own listings, and cannot accept their own requests.
   - Strict request state machine: `Pending` &rarr; `Accepted` / `Rejected` / `Cancelled` &rarr; `Completed`.

5. **Learning Coordination & Peer Feedback**:
   - Session scheduler with video meeting links (Google Meet, Jitsi) or campus room locations.
   - Verified 5-star peer reviews unlocked **exclusively** after an exchange is marked completed.

---

## Project Structure

```text
SkillSwap/
├── app.py                     # Flask application routes, auth, matching & handlers
├── models.py                  # SQLAlchemy ORM models & database seed logic
├── requirements.txt           # Python dependencies
├── README.md                  # Project overview & execution instructions
├── PROJECT_REPORT.md          # Comprehensive Academic Project Report (Chapters 1-5)
├── .env.example               # Environment variables configuration template
├── test_skillswap.py          # Automated test suite (Functional, Auth, DB, State Machine)
│
├── instance/
│   └── skillswap.db           # SQLite persistent database (created automatically)
│
├── templates/
│   ├── base.html              # Unified layout with navbar, footer, flash toasts
│   ├── index.html             # Landing Page with Hero & live catalog preview
│   ├── login.html             # Login module with password toggle & validation
│   ├── signup.html            # Registration module with password strength meter
│   ├── dashboard.html         # User dashboard with real DB stats & recommendations
│   ├── learn.html             # Skill discovery catalog with multi-filters & search
│   ├── teach.html             # Skill publishing, management, edit modal & status toggles
│   ├── skill_exchange.html    # Rule-based matching engine & proposal modal
│   ├── skill_details.html     # Detailed syllabus, outcomes, reviews & request CTA
│   ├── profile.html           # Public / Private profile with ratings & skills
│   ├── edit_profile.html      # Profile editing with dynamic learning interest tags
│   ├── requests.html          # Request management tabs, scheduling & reviews
│   ├── request_details.html   # Detailed request view, session history & participant cards
│   ├── workflow.html          # Interactive 7-stage visual system workflow
│   └── settings.html          # Password change, preferences, privacy & logout
│
└── static/
    ├── css/
    │   └── style.css          # Dark Glassmorphism CSS design system
    └── js/
        ├── common.js          # Navigation, modals, alerts, password toggle
        ├── auth.js            # Login / Signup form validation & password strength
        ├── dashboard.js       # Live search filtering for recommendations
        ├── learn.js           # Catalog filtering & Request to Learn modal
        ├── teach.js           # Edit skill modal population & delete confirmations
        ├── skill_exchange.js  # Match filtering & Propose Exchange modal
        ├── profile.js         # Dynamic skill tag management & avatar selector
        ├── requests.js        # Status transitions, session scheduler & star rating
        └── workflow.js        # Visual workflow stepper & stage highlighting
```

---

## Installation & Execution Instructions

### Prerequisites
- Python 3.9+ (Python 3.12 recommended)
- `pip` (Python package manager)

### 1. Clone or Open Project Directory
Navigate into the `SkillSwap` directory in PowerShell or Terminal:
```bash
cd SkillSwap
```

### 2. (Optional) Create and Activate Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The Flask server will start locally at:
```text
http://127.0.0.1:5000
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Demo Credentials for Evaluators

The database auto-seeds realistic campus student accounts on first startup:

| Student Name | Email Address | Password | Role / Focus |
|:---|:---|:---|:---|
| **Alex Morgan** | `alex.morgan@campus.edu` | `Password123!` | 3rd Year CS &bull; Teaches Python & Web Dev |
| **Sarah Chen** | `sarah.chen@campus.edu` | `Password123!` | Senior Design &bull; Teaches Figma UI/UX |
| **Marcus Vance** | `marcus.vance@campus.edu` | `Password123!` | Grad Student &bull; Teaches Machine Learning |
| **Priya Patel** | `priya.patel@campus.edu` | `Password123!` | Junior IS &bull; Teaches Flutter Mobile Apps |
| **Liam Rodriguez** | `liam.rodriguez@campus.edu` | `Password123!` | Media &bull; Teaches Public Speaking |

*You can also click **Get Started** or **Create Account** to register a new student account at any time.*

---

## Running Automated Tests

A comprehensive automated test suite is included in `test_skillswap.py`. It runs in isolated memory to validate authentication, authorization rules, rule-based matching, CRUD operations, and request state machines:

```bash
python test_skillswap.py
```

Sample output:
```text
........
----------------------------------------------------------------------
Ran 8 tests in 7.721s

OK
```

---

## Academic Documentation

For complete academic project documentation according to design studio requirements, refer to:
- `PROJECT_REPORT.md` — Contains Chapters 1 through 5, system methodology, architectural diagrams, data dictionary, testing verification, and verified peer-to-peer educational references.
