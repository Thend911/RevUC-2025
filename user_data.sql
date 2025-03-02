CREATE TABLE IF NOT EXISTS user_streaks (
    user_id INTEGER PRIMARY KEY,
    last_active DATE,
    streak_count INTEGER
);

CREATE TABLE IF NOT EXISTS user_grades (
    user_id INTEGER,
    course_id INTEGER,
    final_grade REAL,
    PRIMARY KEY (user_id, course_id)
);