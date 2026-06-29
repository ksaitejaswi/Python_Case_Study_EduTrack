from sqlalchemy import func
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload

from .database import Base, engine, get_db, SessionLocal
from .seed import seed_courses

from .models import User, Course, Enrollment,Achievement
from .schemas import (
    UserCreate,
    UserResponse,
    EnrollmentCreate,
    EnrollmentResponse,
    AchievementResponse,
)

# Create FastAPI application
app = FastAPI(title="EduTrack API Prototype")

# Create database tables
Base.metadata.create_all(bind=engine)


# Seed sample courses when application starts
@app.on_event("startup")
def startup():
    db = SessionLocal()
    seed_courses(db)
    db.close()


# -------------------------
# Home API
# -------------------------
@app.get("/")
def home():
    return {"message": "EduTrack API is running!"}


# -------------------------
# Create User
# -------------------------
@app.post("/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        name=user.name,
        email=user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------------
# Get All Users
# -------------------------
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# -------------------------
# Get All Courses
# -------------------------
@app.get("/courses")
def get_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()


# -------------------------
# Enroll User in Course
# -------------------------
@app.post("/enrollments", response_model=EnrollmentResponse)
def create_enrollment(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db)
):

    # Check user exists
    user = (
        db.query(User)
        .filter(User.id == enrollment.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check course exists
    course = (
        db.query(Course)
        .filter(Course.id == enrollment.course_id)
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    # Prevent duplicate active enrollment
    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.user_id == enrollment.user_id,
            Enrollment.course_id == enrollment.course_id,
            Enrollment.status == "active"
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="User already enrolled in this course"
        )

    # Create new enrollment
    new_enrollment = Enrollment(
        user_id=enrollment.user_id,
        course_id=enrollment.course_id
    )

    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)

    return new_enrollment

@app.post("/enrollments/{enrollment_id}/complete-lesson")
def complete_lesson(
    enrollment_id: int,
    db: Session = Depends(get_db)
):

    enrollment = (
        db.query(Enrollment)
        .filter(Enrollment.id == enrollment_id)
        .first()
    )

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found"
        )

    if enrollment.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Course already completed"
        )

    course = (
        db.query(Course)
        .filter(Course.id == enrollment.course_id)
        .first()
    )

    enrollment.completed_lessons_count += 1

    if enrollment.completed_lessons_count >= course.total_lessons:

        enrollment.completed_lessons_count = course.total_lessons
        enrollment.status = "completed"

        from datetime import datetime

        enrollment.completed_at = datetime.utcnow()

        # -----------------------------
        # Fast Starter Achievement
        # -----------------------------
        completed_courses = (
            db.query(Enrollment)
            .filter(
                Enrollment.user_id == enrollment.user_id,
                Enrollment.status == "completed"
            )
            .count()
        )

        if completed_courses == 1:

            exists = (
                db.query(Achievement)
                .filter(
                    Achievement.user_id == enrollment.user_id,
                    Achievement.title == "Fast Starter"
                )
                .first()
            )

            if not exists:
                db.add(
                    Achievement(
                        user_id=enrollment.user_id,
                        title="Fast Starter"
                    )
                )

        # -----------------------------
        # Deep Diver Achievement
        # -----------------------------
        if course.total_lessons >= 10:

            exists = (
                db.query(Achievement)
                .filter(
                    Achievement.user_id == enrollment.user_id,
                    Achievement.title == "Deep Diver"
                )
                .first()
            )

            if not exists:
                db.add(
                    Achievement(
                        user_id=enrollment.user_id,
                        title="Deep Diver"
                    )
                )

    db.commit()
    db.refresh(enrollment)

    return {
        "message": "Lesson completed successfully",
        "completed_lessons": enrollment.completed_lessons_count,
        "status": enrollment.status
    }
@app.get("/users/{user_id}/dashboard")
def user_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    enrollments = (
        db.query(Enrollment)
        .options(joinedload(Enrollment.course))
        .filter(
            Enrollment.user_id == user_id,
            Enrollment.status == "active"
        )
        .all()
    )

    active_courses = []

    for enrollment in enrollments:

        progress = (
            enrollment.completed_lessons_count
            / enrollment.course.total_lessons
        ) * 100

        active_courses.append(
            {
                "course": enrollment.course.title,
                "progress": round(progress, 2)
            }
        )

    achievements = (
        db.query(Achievement)
        .filter(Achievement.user_id == user_id)
        .all()
    )

    return {

        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },

        "active_courses": active_courses,

        "achievements": [
            achievement.title
            for achievement in achievements
        ]

    }
@app.get("/analytics/leaderboard")
def leaderboard(
    db: Session = Depends(get_db)
):

    results = (

        db.query(

            User.id,
            User.name,

            func.sum(
                Enrollment.completed_lessons_count
            ).label("total_lessons")

        )

        .join(
            Enrollment,
            User.id == Enrollment.user_id
        )

        .group_by(
            User.id,
            User.name
        )

        .order_by(
            func.sum(
                Enrollment.completed_lessons_count
            ).desc()
        )

        .limit(5)

        .all()

    )

    leaderboard = []

    for row in results:

        leaderboard.append(

            {
                "user_id": row.id,
                "name": row.name,
                "total_lessons_completed": row.total_lessons
            }

        )

    return leaderboard