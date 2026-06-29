# EduTrack – Micro-Learning Progress & Analytics API

## Project Overview

EduTrack is a RESTful backend API built using **FastAPI**, **SQLite**, and **SQLAlchemy**. It enables users to enroll in courses, track lesson completion, unlock achievements automatically, and view learning analytics.

This project was developed as a prototype for a micro-learning platform.

---

## Technologies Used

* Python 3.10+
* FastAPI
* SQLite
* SQLAlchemy ORM
* Pydantic
* Uvicorn

---

## Project Features

### User Management

* Create new users
* View all registered users

### Course Management

* View available courses
* Automatically seed sample courses

### Enrollment

* Enroll users into courses
* Prevent duplicate active enrollments

### Lesson Progress

* Complete lessons
* Automatically complete courses
* Store completion date

### Achievement System

* Fast Starter
* Deep Diver

### Dashboard

* View user details
* View active courses
* View course progress
* View earned achievements

### Leaderboard

* Displays Top 5 users based on total completed lessons using SQL aggregation.

---

## Project Structure

```
EduTrack/
│
├── app/
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   ├── main.py
│   └── __init__.py
│
├── requirements.txt
├── README.md
├── edutrack.db
└── venv/
```

---

## Installation


### Create Virtual Environment

```bash
python -m venv venv
```

---

### Activate Virtual Environment

Windows

```bash
venv\Scripts\activate
```
---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Run the Server

```bash
uvicorn app.main:app --reload
```

---

## Swagger Documentation

Open:

```
http://127.0.0.1:8000/docs
```

---

## Sample Courses

The application automatically seeds the following courses:

| Course           | Lessons |
| ---------------- | ------- |
| Python Basics    | 5       |
| Intro to FastAPI | 3       |
| SQL 101          | 10      |

---

## Available APIs

### Users

* POST /users
* GET /users

### Courses

* GET /courses

### Enrollments

* POST /enrollments
* POST /enrollments/{enrollment_id}/complete-lesson

### Dashboard

* GET /users/{user_id}/dashboard

### Analytics

* GET /analytics/leaderboard

---

## Achievement Rules

### Fast Starter

Awarded when the user completes their first course.

### Deep Diver

Awarded when the user completes a course containing 10 or more lessons.

---

## Author

Project developed using FastAPI and SQLAlchemy as part of the EduTrack Backend API Case Study.
