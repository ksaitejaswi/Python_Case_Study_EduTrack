from sqlalchemy.orm import Session
from .models import Course


def seed_courses(db: Session):
    # Check if courses already exist
    existing_courses = db.query(Course).count()

    if existing_courses > 0:
        return

    courses = [
        Course(
            title="Python Basics",
            description="Learn Python from scratch",
            total_lessons=5
        ),
        Course(
            title="Intro to FastAPI",
            description="Learn FastAPI fundamentals",
            total_lessons=3
        ),
        Course(
            title="SQL 101",
            description="Learn SQL basics",
            total_lessons=10
        )
    ]

    db.add_all(courses)
    db.commit()