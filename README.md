# Library Management System

A comprehensive library management system built with Python (Django) and PostgreSQL, designed to handle user management, book inventory, transactions, and more.

## Features (Planned & Implemented)

*   **Database Schema:** PostgreSQL backend with tables for Users, Books, Transactions, Fees.
*   **Core Functionality:**
    *   User Management (CRUD)
    *   Inventory Control (Track books with status: available/borrowed/lost)
    *   Fee System (Automatic overdue fee calculation)
    *   Barcode Integration (Generate scannable barcodes - *planned*)
    *   Import/Export (CSV/Excel bulk operations - *planned*)
*   **Admin Features:**
    *   Customizable dashboard (*planned*)
    *   Role-based access (Librarian vs. Admin)
    *   Audit logs (*partially via Django Admin logs*)
*   **API Endpoints (RESTful):**
    *   `/api/users/`
    *   `/api/books/` (with search)
    *   `/api/transactions/` (checkout/return)
    *   JWT Authentication for ERP integration (`/api/token/`, `/api/token/refresh/`)
*   **UI Requirements:**
    *   Responsive Bootstrap interface (*via Django Admin and future templates*)
    *   Admin panel for system configuration (Django Admin)

## Prerequisites

Before you begin, ensure you have the following installed:

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL of this repository
    cd <repository-directory-name> # Replace <repository-directory-name> with the name of the cloned folder
    ```

2.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file and **customize the variables**, especially `DJANGO_SECRET_KEY`. It's crucial for security that you set your own unique `DJANGO_SECRET_KEY`. You can generate a new secret key using an online Django secret key generator or by running the following in a Python shell:
        ```python
        # from django.core.management.utils import get_random_secret_key
        # print(get_random_secret_key())
        ```
    *   You can also adjust database credentials or ports if needed, but the defaults (`POSTGRES_USER=library_user`, `POSTGRES_PASSWORD=library_password`, `POSTGRES_DB=library_db`, `DJANGO_PORT_HOST=8000`, `POSTGRES_PORT_HOST=5433`) are set up to work together for a local setup.

3.  **Build and Run with Docker Compose:**
    *   From the project root directory (where `docker-compose.yml` is located), run:
        ```bash
        docker-compose up --build -d
        ```
    *   This command will:
        *   Build the Docker image for the Django application (if not already built or if changes are detected in `Dockerfile` or related files).
        *   Pull the PostgreSQL image if not already present.
        *   Start the PostgreSQL database service (`db`).
        *   Start the Django web application service (`web`).
        *   The `web` service is configured to automatically apply database migrations upon starting.
        *   The `-d` flag runs the containers in detached mode (in the background). To see logs, you can run `docker-compose logs -f`.

## Running the Application

Once the containers are up and running (you can check status with `docker-compose ps`):

*   **Web Application (Admin Panel):**
    *   Access the Django Admin interface at: `http://localhost:8000/admin/` (or `http://localhost:<your_DJANGO_PORT_HOST>/admin/` if you changed `DJANGO_PORT_HOST` in `.env`).
    *   *(Optional: Add a screenshot of the admin login page here)*
        `![Admin Login Page](assets/images/admin_login_example.png)`
    *   *(Optional: Add a screenshot of the admin dashboard or a model list page here)*
        `![Admin Dashboard Example](assets/images/admin_dashboard_example.png)`

*   **Creating a Superuser:**
    *   To access the admin panel, you'll need a superuser account. Create one by running:
        ```bash
        docker-compose exec web python manage.py createsuperuser
        ```
    *   Follow the prompts to set a username, email (optional), and password.

## API Endpoints and Documentation

*   **API Base URL:** `http://localhost:8000/api/` (or replace `8000` with your `DJANGO_PORT_HOST`)
*   **Swagger UI (Interactive API Documentation):** `http://localhost:8000/swagger/`
    *   *(Optional: Add a screenshot of the Swagger UI page here)*
        `![Swagger UI Example](assets/images/swagger_ui_example.png)`
*   **ReDoc (Alternative API Documentation):** `http://localhost:8000/redoc/`

*   **Authentication:**
    *   Most API endpoints require JWT authentication (this is the default permission in `settings.py`).
    *   Obtain a JWT token by sending a POST request with your superuser (or other created user) credentials to:
        `POST /api/token/`
        **Request Body:**
        ```json
        {
            "username": "yourusername",
            "password": "yourpassword"
        }
        ```
    *   Refresh an expired access token using a POST request to:
        `POST /api/token/refresh/`
        **Request Body:**
        ```json
        {
            "refresh": "your_refresh_token_here"
        }
        ```
    *   To access protected endpoints, include the `access` token in the `Authorization` header:
        `Authorization: Bearer <your_access_token_here>`
    *   You can use the "Authorize" button in the Swagger UI to set the token for testing API calls directly from the browser.

## Stopping the Application

*   To stop the running Docker containers:
    ```bash
    docker-compose down
    ```
*   If you want to remove the data volume for PostgreSQL (useful for a completely clean restart, but **this will delete all database data**):
    ```bash
    docker-compose down -v
    ```

## Running Tests (Placeholder)

*   While specific tests for this project are yet to be written, Django's test runner can be invoked. Once tests are added to the `core` app or other apps, you can run them using:
    ```bash
    docker-compose exec web python manage.py test
    ```
    Or for a specific app:
    ```bash
    docker-compose exec web python manage.py test core
    ```

## Project Structure (Brief Overview)

*   `library_system/`: Main Django project directory containing global settings (`settings.py`), main URL configurations (`urls.py`), and WSGI entry point.
*   `core/`: A Django app containing the core library functionalities:
    *   `models.py`: Database models (User, Book, Transaction, Fee).
    *   `views.py`: API viewsets.
    *   `serializers.py`: Data serializers for API request/response handling.
    *   `urls.py`: API URL routing for the `core` app.
    *   `admin.py`: Configuration for Django admin interface.
    *   `migrations/`: Database migration files.
*   `Dockerfile`: Instructions to build the Docker image for the Django application.
*   `docker-compose.yml`: Defines and configures the multi-container application services (web and database).
*   `requirements.txt`: A list of Python package dependencies for the project.
*   `.env.example`: An example file showing the required environment variables. You should copy this to `.env` and fill in your actual values.
*   `manage.py`: Django's command-line utility for various tasks like running the server, creating migrations, etc.
*   `assets/images/`: Directory for storing static images and screenshots.
    *   `.gitkeep`: Placeholder file to ensure the directory is tracked by Git.
    *   *(You should replace `admin_login_example.png`, `admin_dashboard_example.png`, `swagger_ui_example.png` with actual screenshots after running the application.)*
*   `README.md`: This file.

---

This project is currently under development. More features and refinements will be added over time.
```
