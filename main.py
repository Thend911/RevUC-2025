from canvasapi import Canvas
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Canvas API URL
API_URL = "https://uc.instructure.com/"
# Canvas API key from .env file
API_KEY = os.getenv("API_KEY")
if API_KEY is None:
    raise ValueError("API_KEY not found in environment variables")

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

user = canvas.get_current_user()
print(f"User ID: {user.id}")
print(f"User Name: {user.name}")
print(f"User Email: {user.email if hasattr(user, 'email') else 'Email not available'}")

courses = user.get_courses(enrollment_state="active")

for course in courses:
    print(course.name)


