# COLLEGE DESIGN STUDIO LAB PROJECT REPORT

# SKILLSWAP — A Peer-to-Peer Skill Learning and Exchange Platform
*Learn Together, Grow Together*

---

## CHAPTER 1 — INTRODUCTION

### 1.1 Introduction
The digital transformation of higher education has expanded access to learning resources; however, practical skill acquisition frequently encounters critical socio-economic and pedagogical bottlenecks. While traditional university curricula provide foundational theoretical frameworks, students increasingly require practical, cross-disciplinary competencies—such as modern software development, user experience prototyping, data analysis, and technical communication. 

**SkillSwap — Learn Together, Grow Together** is a peer-to-peer (P2P) skill learning and reciprocal exchange web platform engineered specifically for college students. The platform operates on the pedagogical philosophy that the most effective way to consolidate knowledge is through teaching, and that every student possesses valuable capabilities that can be reciprocally exchanged with peers without financial transactions. Through bilateral skill matching, transparent rule-based compatibility scoring, interactive request lifecycle management, and verified peer feedback, SkillSwap fosters a collaborative campus learning ecosystem.

### 1.2 Problem Statement
Contemporary higher education students face significant challenges in acquiring secondary and interdisciplinary skills:
1. **Commercial Paywalls and Prohibitive Tutor Costs**: Commercial e-learning platforms, bootcamps, and professional tutoring marketplaces demand significant subscription or hourly fees, creating socioeconomic barriers for university students.
2. **Passive, Isolated Learning Experiences**: Pre-recorded video courses suffer from attrition rates exceeding 85%, lacking real-time peer accountability, contextual feedback, and interactive problem solving.
3. **Fragmented Campus Knowledge**: On any given campus, computer science majors seek design guidance, design students seek backend engineering mentorship, and engineering scholars need presentation coaching. However, no centralized, trusted, reciprocal mechanism exists to discover and exchange these complementary capabilities.
4. **Fraudulent and Unverified Online Ratings**: Commercial platforms often suffer from inflated, unverified reviews and anonymous testimonials, reducing trust in peer capabilities.

### 1.3 Objectives
The primary objectives of the SkillSwap project are:
- To design and implement a full-stack, responsive, database-driven peer-to-peer skill exchange platform.
- To eliminate monetary dependencies by establishing a barter-based knowledge exchange mechanism.
- To implement a deterministic, transparent, rule-based matching engine that identifies bilateral reciprocal synergies between student teaching skills and learning interests.
- To enforce robust security, role-based authorization, cryptographic password protection, and anti-CSRF measures.
- To model a formal finite state machine for managing exchange requests (`Pending` &rarr; `Accepted` / `Rejected` / `Cancelled` &rarr; `Completed`).
- To provide scheduling and closed-loop feedback systems where reviews can only be generated following verified session completion.

### 1.4 Existing System
In existing educational environments, students rely on:
- **Commercial EdTech Platforms (Coursera, Udemy, LinkedIn Learning)**: Asynchronous, video-centric platforms charging subscription fees with minimal peer interaction.
- **Freelance Tutoring Platforms (Wyzant, Preply, Superprof)**: Commercial marketplaces where tutors charge hourly rates, pricing out typical undergraduate students.
- **Informal Channels (WhatsApp Groups, Discord Servers, Reddit, Campus Bulletin Boards)**: Unstructured message boards lacking structured skill taxonomies, verified profiles, session schedulers, or accountability mechanisms.

### 1.5 Proposed System
SkillSwap proposes a structured, decentralized peer exchange platform that connects learners and mentors across university departments. Key elements of the proposed system include:
- **Comprehensive User Identity**: Academic profiles capturing institution, major, teaching capabilities, learning goals, availability, and preferred modes (Online, In-Person, Hybrid).
- **Interactive Catalogs**: Public and filtered search interfaces across academic, technological, and creative categories with real database querying.
- **Bilateral Matching Algorithm**: Transparent matching calculating exact reciprocal scores and natural language rationales (e.g., "User A teaches Python which User B wants, and User B teaches Figma which User A wants").
- **Formal Request Workflow**: Finite state machine preventing unauthorized mutations, self-requests, or invalid status progressions.
- **Integrated Session Coordination**: Built-in scheduling with meeting links and prep notes.
- **Closed-Loop Feedback**: Verified ratings and peer reviews linked directly to completed exchanges.

### 1.6 Advantages of Proposed System
1. **Zero Financial Cost**: Learning is demonetized through reciprocal barter.
2. **Pedagogical Reinforcement**: Teaching reinforces conceptual understanding (the "Protégé Effect").
3. **Cross-Departmental Collaboration**: Connects students across Computer Science, Design, Engineering, Business, and Communications.
4. **Data Integrity & Trust**: Built on authentic SQLite database records with authenticated access and verified reviews.
5. **Transparency**: Eliminates misleading AI claims by using deterministic, rule-based matching criteria.

### 1.7 Scope of the Project
The scope encompasses full-stack implementation running locally using Python, Flask, SQLite, and vanilla frontend technologies (HTML5, CSS3, JavaScript). It supports user registration, profile management, skill creation, multi-attribute catalog filtering, reciprocal exchange proposal handling, status state machine management, session scheduling, and peer review submissions. Paid third-party APIs and unnecessary external frameworks are deliberately excluded in favor of clean native standards.

---

## CHAPTER 2 — LITERATURE SURVEY AND EXISTING SYSTEMS

### 2.1 Literature Review
Research in collaborative learning and peer education highlights several established pedagogical frameworks:
- **Vygotsky's Zone of Proximal Development (ZPD)**: Demonstrates that peer learners often provide more accessible explanations than senior experts because their cognitive state is closer to that of the learner.
- **The Protégé Effect (Chase et al., 2009)**: Confirms that students make greater cognitive effort to learn and structure material when they prepare to teach fellow peers than when studying solely for personal examination.
- **Reciprocal Peer Tutoring (RPT) (Fantuzzo et al., 1989)**: Establishes that alternating roles between tutor and tutee maximizes academic achievement, psychological well-being, and social integration.
- **Recommender Systems in E-Learning (Manouselis et al., 2011)**: Emphasizes the importance of transparency and explanation in educational recommendation engines over black-box machine learning models, ensuring student trust and agency.

### 2.2 Research Gap
While commercial platforms successfully connect consumers with paid experts and social platforms facilitate unstructured conversations, there exists a significant gap in platforms that combine:
1. Academic identity verification,
2. Bilateral reciprocal skill matching,
3. Formal lifecycle state enforcement, and
4. Closed-loop post-session peer review verification.

SkillSwap fills this gap by formalizing campus barter learning within a single, secure web application.

### 2.3 Existing Systems Analysis
| Feature | Commercial MOOCs | Freelance Tutors | Campus Forums (Discord/Reddit) | SkillSwap (Proposed) |
|:---|:---|:---|:---|:---|
| **Cost** | Subscription / Paywall | Hourly ($20 - $80/hr) | Free | **100% Free / Reciprocal** |
| **Interaction** | Passive / Pre-recorded | 1-on-1 Paid | Unstructured Text | **1-on-1 Structured Sessions** |
| **Matching** | Search Keyword Only | Location / Price Filter | Manual Browsing | **Deterministic Reciprocal Engine** |
| **Accountability** | Quizzes / Multiple Choice | Payment escrow | None | **Request Lifecycle & Sessions** |
| **Reviews** | Public / Open to Spam | Commercial Testimonials | Unverified Comments | **Verified Post-Exchange Reviews** |

### 2.4 Limitations of Existing Systems
- **Financial Exclusion**: Students unable to afford tutoring are left behind.
- **Lack of Reciprocity**: Existing systems treat learners solely as passive consumers rather than knowledgeable contributors.
- **Noise and Search Friction**: Informal message boards lack structured taxonomies, requiring tedious manual coordination.

---

## CHAPTER 3 — SYSTEM METHODOLOGY AND DESIGN

### 3.1 System Design and Development
SkillSwap adopts an iterative, component-driven software engineering methodology conforming to the Model-View-Controller (MVC) architectural pattern:
- **Model Layer**: SQLAlchemy ORM classes mapping entities directly to persistent SQLite tables.
- **View Layer**: Semantic HTML5 templates rendered via Jinja2 engine, styled with Vanilla CSS3 glassmorphism, and animated via Vanilla JavaScript.
- **Controller Layer**: Python Flask routes managing request routing, authentication guards, input sanitization, and state transitions.

### 3.2 System Architecture
```
+-----------------------------------------------------------------------+
|                         PRESENTATION LAYER                            |
|  - HTML5 Semantic Structure                                           |
|  - Vanilla CSS3 Glassmorphism System (Deep Navy, Violet, Cyan)        |
|  - Vanilla JavaScript DOM Controllers (common.js, auth.js, etc.)      |
+-----------------------------------------------------------------------+
                                  |
                           HTTP / Fetch API
                                  |
+-----------------------------------------------------------------------+
|                          APPLICATION LAYER                            |
|  - Flask Application Core (app.py)                                     |
|  - Session-Based Authentication & Password Hashing (Werkzeug)         |
|  - Rule-Based Reciprocal Matching Engine                              |
|  - Finite State Machine Request Processor                             |
|  - CSRF Security & Server-Side Input Validators                       |
+-----------------------------------------------------------------------+
                                  |
                            SQLAlchemy ORM
                                  |
+-----------------------------------------------------------------------+
|                           DATABASE LAYER                              |
|  - SQLite Persistent Database (instance/skillswap.db)                 |
|  - Relational Schema: Users, Skills, Interests, Requests, Sessions,   |
|    Reviews                                                            |
+-----------------------------------------------------------------------+
```

### 3.3 Presentation Layer
The presentation layer is styled with a custom futuristic design system featuring:
- **Color Palette**: Deep Navy (`#0A0E1A`), Near Black (`#050811`), Royal Purple (`#7000FF`), Violet (`#8B5CF6`), Electric Blue (`#3B82F6`), and Cyan Highlights (`#00F2FE`).
- **Glassmorphism**: Backdrop blur filters (`blur(14px)`), translucent container fills (`rgba(16, 23, 41, 0.75)`), and glowing borders.
- **Responsive Layout**: CSS Grid and Flexbox responsive breakpoints adapting from mobile screens (320px) up to ultra-wide displays.

### 3.4 Application Layer
The application layer manages:
- **Authentication**: Cryptographic password hashing (`scrypt` / `pbkdf2:sha256`) and session tokens.
- **Route Authorization**: Decorator `@login_required` protecting internal pages.
- **Matching Algorithm**: Deterministic calculation cross-referencing teaching skills and learning interests.
- **State Machine**: Restricting invalid state modifications.

### 3.5 Database Layer
Implemented with SQLite via SQLAlchemy. Database tables utilize foreign key constraints, cascading deletes, indexing on lookup columns (`username`, `email`, `user_id`, `status`), and computed relational properties.

### 3.6 Module Structure
1. **Landing Module** (`/`): Public portal introducing core pillars and live catalog preview.
2. **Authentication Module** (`/login`, `/signup`, `/logout`): Registration with password strength meter and login validation.
3. **Dashboard Module** (`/dashboard`): Authenticated hub displaying real database statistics, recommendations, and recent requests.
4. **Learn Module** (`/learn`): Skill discovery with multi-parameter filtering and "Request to Learn" modal.
5. **Teach Module** (`/teach`): Course authoring, editing, status pausing, and listing deletion.
6. **Skill Exchange Module** (`/skill-exchange`): Matching engine displaying compatibility percentages and exchange proposals.
7. **Skill Details Module** (`/skill/<id>`): Deep syllabus view, prerequisites, and instructor bio.
8. **Profile Module** (`/profile`, `/profile/<username>`, `/profile/edit`): Student profile, dynamic interest chips, and reviews.
9. **Request Management Module** (`/requests`, `/request/<id>`): Lifecycle tracking, status transitions, scheduling, and peer reviews.
10. **Workflow Module** (`/workflow`): Interactive 7-stage visual lifecycle diagram.
11. **Settings Module** (`/settings`): Password updates, notifications, and privacy options.

### 3.7 System Workflow
The student journey traverses 7 distinct phases:
1. **Account Creation**: Student enters credentials; password is cryptographically hashed; record is saved to SQLite.
2. **Profile Setup**: Student enters academic major, learning wishlist, teaching topics, and preferred learning modes.
3. **Skill Discovery**: Student searches and filters active peer listings in the Learn catalog.
4. **Skill Matching**: System computes bilateral matches between teaching skills and learning interests.
5. **Request Management**: Proposals are logged as `pending`; recipient accepts or rejects; status updates atomically.
6. **Learning Exchange**: Accepted peers schedule sessions, set meeting links, and conduct 1-on-1 collaborative study.
7. **Feedback**: Completed exchange unlocks peer review; rating and comment update the peer's public profile.

### 3.8 Database Design & Data Dictionary
The relational schema comprises 6 primary models:

#### Table: `users`
| Column | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key | Unique user identifier |
| `full_name` | String(100) | Not Null | Student's full name |
| `username` | String(50) | Unique, Not Null, Indexed | Unique handle |
| `email` | String(120) | Unique, Not Null, Indexed | Campus email |
| `password_hash` | String(255) | Not Null | Hashed password string |
| `institution` | String(150) | Default | College or university name |
| `department` | String(100) | Default | Academic major / department |
| `biography` | Text | Nullable | Student personal bio |
| `preferred_mode` | String(50) | Default: 'Online' | Online, In-Person, Hybrid |
| `preferred_language`| String(50) | Default: 'English' | Preferred language |
| `availability_days` | String(100) | Default | Available meeting days |
| `availability_times`| String(100) | Default | Available meeting times |
| `created_at` | DateTime | Default UTC | Account creation timestamp |

#### Table: `skills`
| Column | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key | Unique skill offering identifier |
| `user_id` | Integer | Foreign Key (`users.id`), Not Null | Instructor user ID |
| `title` | String(120) | Not Null | Course title |
| `category` | String(60) | Not Null, Indexed | Taxonomy category |
| `description` | Text | Not Null | Detailed syllabus and prerequisites |
| `experience_level` | String(50) | Not Null | Beginner, Intermediate, Advanced, Expert |
| `teaching_language`| String(50) | Default: 'English' | Instructional language |
| `learning_mode` | String(50) | Default: 'Online' | Online, In-Person, Hybrid |
| `session_duration` | String(50) | Default: '45-60 mins' | Typical duration |
| `available_days` | String(120) | Default | Days offered |
| `available_times` | String(120) | Default | Time slots |
| `resources` | Text | Nullable | Curated materials and starter repos |
| `outcomes` | Text | Nullable | Target learning outcomes |
| `status` | String(20) | Default: 'active' | 'active' or 'paused' |
| `created_at` | DateTime | Default UTC | Listing timestamp |

#### Table: `learning_interests`
| Column | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key | Interest identifier |
| `user_id` | Integer | Foreign Key (`users.id`), Not Null | Student ID |
| `skill_name` | String(100) | Not Null | Target skill name |
| `category` | String(60) | Nullable | Associated category |

#### Table: `exchange_requests`
| Column | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key | Request identifier |
| `sender_id` | Integer | Foreign Key (`users.id`), Not Null | Request initiator |
| `recipient_id` | Integer | Foreign Key (`users.id`), Not Null | Targeted instructor |
| `request_type` | String(20) | Not Null | 'learn' or 'exchange' |
| `teach_skill_id` | Integer | Foreign Key (`skills.id`), Nullable | Offered skill (for reciprocal exchange) |
| `learn_skill_id` | Integer | Foreign Key (`skills.id`), Not Null | Requested skill |
| `message` | Text | Not Null | Learning goal / intro message |
| `preferred_days` | String(100) | Default | Proposed days |
| `preferred_time` | String(100) | Default | Proposed time |
| `learning_mode` | String(50) | Default: 'Online' | Mode |
| `status` | String(20) | Default: 'pending', Indexed | 'pending', 'accepted', 'rejected', 'cancelled', 'completed' |
| `created_at` | DateTime | Default UTC | Creation timestamp |
| `updated_at` | DateTime | Default UTC | Last modification timestamp |

#### Table: `sessions`
| Column | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key | Session identifier |
| `exchange_request_id` | Integer | Foreign Key (`exchange_requests.id`), Not Null | Linked exchange |
| `scheduled_date` | String(50) | Not Null | Scheduled calendar date |
| `scheduled_time` | String(50) | Not Null | Scheduled meeting time |
| `duration` | String(50) | Default: '60 mins' | Meeting length |
| `meeting_mode` | String(50) | Default: 'Online' | Video or In-Person |
| `meeting_link` | String(255) | Default | Video URL or campus room |
| `notes` | Text | Nullable | Prep notes and agenda |
| `status` | String(20) | Default: 'scheduled' | Session status |

#### Table: `reviews`
| Column | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | Integer | Primary Key | Review identifier |
| `exchange_request_id` | Integer | Foreign Key (`exchange_requests.id`), Not Null | Completed exchange |
| `reviewer_id` | Integer | Foreign Key (`users.id`), Not Null | Review author |
| `reviewed_user_id`| Integer | Foreign Key (`users.id`), Not Null | Evaluated peer |
| `rating` | Integer | Not Null (1 to 5) | Star rating |
| `comment` | Text | Not Null | Qualitative peer feedback |
| `created_at` | DateTime | Default UTC | Review timestamp |

---

## CHAPTER 4 — IMPLEMENTATION AND TESTING

### 4.1 Frontend Implementation
The SkillSwap frontend is developed using HTML5, CSS3, and Vanilla JavaScript to provide a responsive and user-friendly interface. The frontend contains separate pages for user authentication, dashboard, skill discovery, skill teaching, skill exchange, profile management, request management, workflow visualization, and settings. The interface uses a consistent modern design with responsive layouts, skill cards, navigation components, forms, status indicators, and interactive elements. JavaScript is used for client-side validation and dynamic interactions, while the frontend communicates with the Flask backend for retrieving and updating application data.

#### Frontend Technologies Used
• HTML5  
• CSS3  
• Vanilla JavaScript  
• Responsive Web Design  
• Fetch API  

#### Features Implemented in Frontend
• User registration and login  
• Dashboard  
• Skill discovery  
• Skill teaching  
• Skill exchange matching  
• User profile management  
• Request management  
• System workflow visualization  
• Settings  
• Responsive navigation  

### 4.2 Backend Implementation
The SkillSwap backend is developed using Python and Flask to manage application logic, authentication, database operations, skill matching, and request processing. Flask routes handle communication between the frontend and database. Secure password hashing and session-based authentication are used to protect user accounts and restricted modules. Server-side validation and authorization checks ensure that users can perform only permitted operations.

#### Backend Technologies Used
• Python  
• Flask  
• SQLAlchemy  
• Flask Sessions  
• Password Hashing  
• REST-style routes  

#### Backend Features
• User authentication  
• User registration  
• Skill management  
• Skill matching  
• Exchange request processing  
• Profile management  
• Database operations  
• Authorization  
• Session management  

### 4.3 Database Implementation
SQLite is used as the database for storing SkillSwap application data. SQLAlchemy is used to communicate with the database and manage relationships between users, skills, learning interests, exchange requests, sessions, and reviews. The database is initialized automatically when required and existing records are preserved when the application starts.

#### Database Information Stored
• User details  
• Teaching skills  
• Learning interests  
• Skill listings  
• Exchange requests  
• Learning sessions  
• Reviews and ratings  
• User preferences  

### 4.4 Module Implementation Details
- **Deterministic Rule-Based Matching Algorithm**:
  Cross-references student teaching skill sets $S_{teach}$ and learning interests $S_{learn}$. For users $A$ and $B$, if $(S_{teach}^A \cap S_{learn}^B \neq \emptyset) \land (S_{teach}^B \cap S_{learn}^A \neq \emptyset)$, a **Strong Reciprocal Match** is generated with a baseline score of 95 points. Alignment of preferred learning mode and language provides additional compatibility increments (+3 for mode, +2 for language). If only one directional intersection exists, a **Partial Match** is declared.
- **Request State Machine Implementation**:
  Governed by `ExchangeRequest.can_transition_to(new_status, user_id)`. Restricts actions: only the intended recipient can accept/reject `pending` requests; only the initiator can cancel `pending` requests; either participant can mark an `accepted` exchange as `completed` or `cancelled`.

### 4.5 Testing and Validation
Comprehensive automated tests were conducted using Python's `unittest` framework (`test_skillswap.py`). All test suites passed successfully:

| Test Case | Description | Expected Outcome | Result |
|:---|:---|:---|:---|
| `test_database_seeded_properly` | Database automatic initialization | Auto-populates 5 users & 6 skills without errors | **PASS** |
| `test_password_hashing` | Hashing verification | Password hashes non-reversible; correct hash verifies | **PASS** |
| `test_user_registration` | Valid registration workflow | Creates unique user record and redirects to login | **PASS** |
| `test_login_and_logout` | Session management | Sets session on valid login; denies on invalid; clears on logout | **PASS** |
| `test_reciprocal_matching_algorithm` | Algorithm correctness | Identifies reciprocal match between Alex & Sarah with score $\ge 90\%$ | **PASS** |
| `test_cannot_request_own_skill` | Authorization security | Blocks user from submitting request to their own skill | **PASS** |
| `test_skill_crud_and_owner_authorization` | Skill ownership guard | Owner can edit; non-owner attempt is rejected | **PASS** |
| `test_request_lifecycle_and_session_and_review` | End-to-end lifecycle | Request &rarr; Accept &rarr; Schedule &rarr; Complete &rarr; Review published | **PASS** |

---

## CHAPTER 5 — CONCLUSION AND FUTURE ENHANCEMENTS

### 5.1 Conclusion
The **SkillSwap — Learn Together, Grow Together** platform demonstrates the viability of a decentralized, peer-to-peer knowledge exchange ecosystem tailored for university environments. By replacing commercial transaction fees with reciprocal peer barter, students across disciplines are empowered to acquire practical skills while simultaneously reinforcing their own subject mastery through teaching. 

The architecture strictly adheres to modern engineering standards: semantic HTML5, pure CSS3 glassmorphism, native Vanilla JavaScript interactions, Python Flask application routing, and persistent SQLite relational data storage via SQLAlchemy. Every functional requirement—from cryptographic security and deterministic matching to request lifecycle state machines and closed-loop peer reviews—has been implemented, verified, and demonstrated with real database records.

### 5.2 Future Enhancements
Future iterations of SkillSwap may incorporate:
1. **Real-Time WebSocket Messaging**: Integrating WebSockets for peer chat coordination during scheduled sessions.
2. **Calendar Integration (iCal / Google Calendar)**: Automated generation of `.ics` invite files upon session confirmation.
3. **Campus Badge & Credential Verification**: Digital credential issuance (e.g., OpenBadges standard) recognizing students who complete significant hours of peer mentoring.
4. **Offline Mobile Application**: React Native or Flutter mobile client communicating with the existing Flask REST API routes.

---

## REFERENCES

1. **Boud, D., Cohen, R., & Sampson, J. (2014).** *Peer Learning in Higher Education: Learning from and with Each Other.* Routledge.
2. **Chase, C. C., Chin, D. B., Oppezzo, M. A., & Schwartz, D. L. (2009).** Teachable agents and the protégé effect: Increasing the effort towards learning. *Journal of Science Education and Technology*, 18(4), 334–352.
3. **Fantuzzo, J. W., Riggio, R. E., Connelly, S., & Dimeff, L. A. (1989).** Effects of reciprocal peer tutoring on academic achievement and psychological adjustment: A component analysis. *Journal of Educational Psychology*, 81(2), 173–177.
4. **Topping, K. J. (1996).** The effectiveness of peer tutoring in higher education: A typological review. *Higher Education*, 32(3), 321–345.
5. **Vygotsky, L. S. (1978).** *Mind in Society: The Development of Higher Psychological Processes.* Harvard University Press.
6. **Manouselis, N., Drachsler, H., Vuorikari, R., Hummel, H., & Koper, R. (2011).** Recommender systems in technology enhanced learning. *Recommender Systems Handbook*, Springer, 387–415.
7. **Grinberg, M. (2018).** *Flask Web Development: Developing Web Applications with Python.* O'Reilly Media.
8. **Fielding, R. T. (2000).** *Architectural Styles and the Design of Network-based Software Architectures.* Doctoral dissertation, University of California, Irvine.
