from flask import Flask, redirect, url_for, session, request, render_template
from canvasapi import Canvas
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables from .env file
load_dotenv()

# Canvas API URL
#CANVAS_API_URL = os.getenv("CANVAS_API_URL")
CANVAS_API_URL = "https://uc.instructure.com/"

@app.route('/')
def index():
    if 'access_token' in session:
        access_token = session['access_token']
        canvas = Canvas(CANVAS_API_URL, access_token)
        try:
            user = canvas.get_current_user()
            print(f"User ID: {user.id}")
            print(f"User Name: {user.name}")

            # Fetch a single course and its grades
            courses = user.get_courses(enrollment_state="active")
            if courses:
                course = courses[0]  # Get the first course for testing
                assignments = course.get_assignments()
                grades = []
                for assignment in assignments:
                    submission = assignment.get_submission(user.id)
                    if submission:
                        grades.append({
                            'assignment_name': assignment.name,
                            'score': submission.score,
                            'max_score': assignment.points_possible
                        })
                return render_template('index.html', user=user, course=course, grades=grades)
            else:
                return render_template('index.html', user=user, error="No active courses found.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('index.html', error=str(e))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        access_token = request.form['access_token']
        session['access_token'] = access_token
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)