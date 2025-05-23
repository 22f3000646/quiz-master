---

# Quiz Masters App

IITM BS MAD 1 Project .A quiz platform consisting of a admin and users who can find give and see results of quiz 
The Quiz Masters App is a web application designed to facilitate creating and managing quizzes. It provides a user-friendly interface for both quiz creation and participation.

## Features

- **Quiz Creation**: Easily create quizzes with customizable questions and answers. 
- **User Management**: Register users and manage their access to quizzes.
- **Quiz Taking**: Participants can take quizzes online with personalized summary.
- **Scoring**: Automatic scoring and results generation.
- **Admin Dashboard**: Admins can manage quizzes, view results, add subjects,etc.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: SQLite (for development)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/22f3000646/quiz-masters.git
   ```


2. Create virtual environment :
  ```
  python -m venv env
  ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up secret key in config.py:
   - SECRET_KEY = '***********'

4. Initialize the database:
   ```
   database will be created on running the application with default admin 
   ```

5. Run the application:
   ```
   python app.py
   ```

The app should now be running on `http://localhost:5000`.

## Usage

- Navigate to `http://localhost:5000` in your web browser.
- Register as a user or log in as an admin.
- Create quizzes, manage participants, and view quiz results from the dashboard.
- Participants can take quizzes by accessing the provided quiz links.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.


## Acknowledgments

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---
