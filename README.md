<img width="6912" height="3456" alt="Alfredo Torres (1)" src="https://github.com/user-attachments/assets/42ceccf1-b706-4188-83b8-2de9591002de" />

# Rake

> **A modern learning platform built for structured, interactive education.**

Rake is a web-based learning platform that combines course management, modular lessons, quizzes, and guided teaching into a single streamlined experience. It provides learners with an intuitive dashboard while giving educators the tools to organize content and monitor progress.

---

## Overview

Traditional online courses often separate lessons, assessments, and teaching into different systems. Rake brings them together in one platform, allowing students to progress through structured learning paths while interacting with course content and completing assessments along the way.

---

## Features

### User Accounts

- Secure authentication
- Personalized dashboards
- Session management
- Individual learning progress

### Course Management

- Create and organize courses
- Structured learning paths
- Modular course content
- Scalable course organization

### Learning Modules

Break courses into manageable lessons that guide students through material step by step.

### Quiz System

- Interactive assessments
- Multiple questions per module
- Progress tracking
- Performance evaluation

### Teaching Sessions

Dedicated teaching sessions provide a space for guided learning, allowing students to engage with instructional content beyond static lessons.

### Dashboard

A centralized dashboard allows users to:

- View enrolled courses
- Continue learning where they left off
- Track completed modules
- Access quizzes and teaching sessions

---

## Platform Architecture

```
Dashboard
│
├── Courses
│     ├── Modules
│     │      └── Quizzes
│     │
│     └── Learning Progress
│
└── Teaching Sessions
```

---

## Built With

- Flask
- SQLAlchemy
- Flask-Login
- Flask-Migrate
- Flask-Bcrypt
- HTML
- CSS
- JavaScript

---

## Design Goals

Rake is designed around three principles:

- **Simple** — Easy to navigate and focused on learning.
- **Structured** — Courses are organized into clear, logical modules.
- **Interactive** — Learning is reinforced through quizzes and guided teaching sessions.

---

## Future Vision

Rake is built with extensibility in mind. Future enhancements may include:

- AI-assisted tutoring
- Rich multimedia lessons
- Real-time collaboration
- Analytics and learning insights
- Instructor tools
- Assignment submissions
- Certificates and achievements

---

## License

MIT License
