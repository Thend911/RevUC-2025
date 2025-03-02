from flask import Flask, redirect, url_for, session, request, render_template
from canvasapi import Canvas
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Load environment variables from .env file
load_dotenv()

# Canvas API URL
CANVAS_API_URL = "https://uc.instructure.com/"

# Connect to SQLite database
connection = sqlite3.connect('database.db', check_same_thread=False)
cursor = connection.cursor()

# Create user_streaks and user_grades tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_streaks (
    user_id INTEGER PRIMARY KEY,
    last_active TEXT,
    streak_count INTEGER
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_grades (
    user_id INTEGER,
    course_id INTEGER,
    final_grade REAL,
    PRIMARY KEY (user_id, course_id)
)
''')
connection.commit()

@app.route('/')
def index():
    if 'access_token' in session:
        access_token = session['access_token']
        canvas = Canvas(CANVAS_API_URL, access_token)
        try:
            user = canvas.get_current_user()
            print(f"User ID: {user.id}")
            print(f"User Name: {user.name}")

            # Fetch all courses and their grades
            courses = user.get_courses(enrollment_state="active")

            course_grades = []
            if courses:
                for course in courses:
                    # Check if the grade is already stored in the database
                    cursor.execute('SELECT final_grade FROM user_grades WHERE user_id = ? AND course_id = ?', (user.id, course.id))
                    row = cursor.fetchone()
                    if row:
                        final_grade = row[0]
                    else:
                        assignments = course.get_assignments()
                        
                        grades = {'total':0, 'total_possible':0}

                        for assignment in assignments:
                            submission = assignment.get_submission(user.id)

                            if submission and hasattr(submission, 'score') and submission.score is not None:
                                if not assignment.points_possible:
                                    continue
                                grades['total_possible'] += assignment.points_possible
                                grades['total'] += submission.score

                        if grades['total'] == 0:
                            final_grade = 0
                        else:
                            final_grade = round((grades['total'] / grades['total_possible']) * 100, 2)
                        
                        # Store the grade in the database
                        cursor.execute('INSERT OR REPLACE INTO user_grades (user_id, course_id, final_grade) VALUES (?, ?, ?)', (user.id, course.id, final_grade))
                        connection.commit()

                    course_grades.append({'course': course, 'final_grade': final_grade})
                    print(f"Course: {course.name}, Final Grade: {final_grade}")

                # Update user streak
                cursor.execute('SELECT last_active, streak_count FROM user_streaks WHERE user_id = ?', (user.id,))
                row = cursor.fetchone()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                if row:
                    last_active, streak_count = row
                    last_active = last_active.split('.')[0]  # Remove milliseconds
                    last_active = datetime.strptime(last_active, '%Y-%m-%d %H:%M:%S')
                    now_dt = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                    if last_active < now_dt - timedelta(seconds=10):
                        if last_active >= now_dt - timedelta(seconds=20):
                            streak_count += 1
                        else:
                            streak_count = 1
                    cursor.execute('UPDATE user_streaks SET last_active = ?, streak_count = ? WHERE user_id = ?', (now, streak_count, user.id))
                else:
                    streak_count = 1
                    cursor.execute('INSERT INTO user_streaks (user_id, last_active, streak_count) VALUES (?, ?, ?)', (user.id, now, streak_count))
                connection.commit()

                return render_template('homepage.html', user=user, course_grades=course_grades, streak_count=streak_count)
            else:
                return render_template('homepage.html', user=user, error="No active courses found.")
        except Exception as e:
            print(f"An error occurred: {e}")
            return render_template('homepage.html', error=str(e))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        access_token = request.form['access_code']
        session['access_token'] = access_token
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('access_token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)