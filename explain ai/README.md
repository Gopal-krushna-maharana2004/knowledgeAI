
# Student Knowledge Predictor (Explain AI)

Predict Your Knowledge. Empowering students to track their progress through AI-driven assessments and web-integrated topic research.

## Project Overview
This is a Flask-based web application designed to help students evaluate their knowledge on various subjects. The application features a chat-based assessment interface, real-time web scraping for topic research, and an automated validation system using Wikipedia data.

## Key Features
- **User Authentication**: Secure register/login system for students.
- **Dynamic Assessment**: Chat-based quiz system with voice and text input.
- **Web Scraping Integration**: 
    - Fetches real-time summaries for topics from Wikipedia.
    - Validates student answers by searching for evidence in web content.
- **Assessment History**: Tracks user scores and history of assessments.
- **Modern UI**: Dark mode, glassmorphism, and responsive design for a premium experience.

## Tech Stack
- **Backend**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Database**: [SQLAlchemy](https://www.sqlalchemy.org/) (SQLite)
- **Scraping**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) & [Requests](https://requests.readthedocs.io/)
- **Frontend**: Vanilla JS, HTML5, CSS3 (Glassmorphism design)

---

## How to Run the Project (Step-by-Step)

### 1. Prerequisites
Ensure you have Python installed on your system. You can check by running:
```bash
python --version
```

### 2. Clone/Open the Project Directory
Navigate to the project folder `d:\explain ai` in your terminal.

### 3. Install Dependencies
Install the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Execute the main application file:
```bash
python app.py
```

### 5. Access the Web App
Once the server starts, open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

### 6. Start Using
- **Register** a new account.
- **Configure** an assessment (Topic, Subject, Number of Questions).
- **Start** the session and interact with the bot!

---

Developed with ❤️ using AI.
