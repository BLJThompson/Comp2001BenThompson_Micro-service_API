
# COMP2001 Trail Management System

## Description

This project is a Flask-based Trail Management System developed for the COMP2001 coursework. 
It allows users to manage trails, features, and user authentication with role-based permissions. 
The application is Dockerized for deployment and integrates with a Microsoft SQL Server database.

## Features

- User authentication and role-based access control.
- CRUD operations for trails and their associated features.
- Microsoft SQL Server as the database backend.
- Dockerized deployment for portability.

## Project Structure

```plaintext
.
├── app.py                # Entry point of the Flask application.
├── auth.py               # Handles user authentication and session management.
├── config.py             # Configuration for the application, including database setup.
├── databasebuild.py      # Script to build and populate the database with sample data.
├── features.py           # API endpoints and logic for managing features.
├── models.py             # ORM models for users, trails, features, and their relationships.
├── permissions.py        # Role-based permission handling.
├── requirements.txt      # Python dependencies for the application.
├── swagger.yml           # API documentation using the OpenAPI specification.
├── trails.py             # API endpoints and logic for managing trails.
└── Dockerfile            # Docker configuration for building and running the application.
```

## Prerequisites

- Python 3.9 or above.
- Docker Desktop (for containerization).
- Microsoft SQL Server (remote or local).

## Installation

### Local Development

1. Clone the repository:
    ```bash
    git clone https://github.com/YourUsername/YourRepoName.git
    cd YourRepoName
    ```

2. Create a virtual environment and install dependencies:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    pip install -r requirements.txt
    ```

3. Run the Flask application:
    ```bash
    python app.py
    ```

4. Access the application at `http://localhost:8000`.

### Docker Deployment

1. Build the Docker image:
    ```bash
    docker build -t comp2001_app .
    ```

2. Run the Docker container:
    ```bash
    docker run -p 8000:8000 comp2001_app
    ```

3. Access the application at `http://localhost:8000`.

### Pull from Docker Hub

Alternatively, pull the pre-built Docker image from Docker Hub:
```bash
docker pull benthompson411/comp2001_app
docker run -p 8000:8000 benthompson411/comp2001_app
```

## API Documentation

The API is documented using OpenAPI (Swagger). Once the application is running, access the documentation at:
```
http://localhost:8000/api/ui
```

## Database

The application uses Microsoft SQL Server as the backend. The database connection is configured in `config.py`.

Sample data is populated via the `databasebuild.py` script. Run this script to initialize the database with users, trails, and features.

## Authors

- Ben Thompson

## Repository Link

[GitHub Repository]https://github.com/BLJThompson/Comp2001BenThompson_Micro-service_API

## Docker Image

Docker Hub: `benthompson411/comp2001_app`
