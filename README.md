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

Before you begin, ensure you have the following installed on your system:

*   **Python:** Version 3.9 or higher. You can download it from [python.org](https://www.python.org/downloads/).
*   **PostgreSQL:** A running PostgreSQL server (version 12 or higher recommended). Installation guides can be found on [postgresql.org](https://www.postgresql.org/download/). You will need to be able to create a database and a user for this application.
*   **pip:** Python package installer (usually comes with Python).
*   **venv:** Module for creating virtual environments (usually comes with Python).
*   **Git:** For cloning the repository.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL of this repository
    cd <repository-directory-name> # Replace <repository-directory-name> with the name of the cloned folder
    ```

2.  **Create and Activate a Python Virtual Environment:**
    *   It's highly recommended to use a virtual environment to manage project dependencies.
    *   Navigate to the project root directory:
        ```bash
        python -m venv venv  # Create a virtual environment named 'venv'
        ```
    *   Activate the virtual environment:
        *   On macOS and Linux:
            ```bash
            source venv/bin/activate
            ```
        *   On Windows:
            ```bash
            .\venv\Scripts\activate
            ```
    *   Your shell prompt should change to indicate that the virtual environment is active (e.g., `(venv) Your-Computer:...$`).

3.  **Install Dependencies:**
    *   With the virtual environment activated, install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```

4.  **Configure PostgreSQL Database:**
    *   Ensure your PostgreSQL server is running.
    *   You need to create a database and a user for this application. You can do this using `psql` or a GUI tool like pgAdmin.
        *   **Example using `psql`:**
            ```sql
            -- Connect to PostgreSQL as a superuser (e.g., postgres)
            -- psql -U postgres

            CREATE DATABASE library_db;
            CREATE USER library_user WITH PASSWORD 'library_password'; -- Choose a strong password!
            ALTER ROLE library_user SET client_encoding TO 'utf8';
            ALTER ROLE library_user SET default_transaction_isolation TO 'read committed';
            ALTER ROLE library_user SET timezone TO 'UTC';
            GRANT ALL PRIVILEGES ON DATABASE library_db TO library_user;
            ```
            *Note: You might need to grant connect privileges or other specific permissions depending on your PostgreSQL setup.*

5.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file with a text editor and **customize the variables**:
        *   `DJANGO_SECRET_KEY`: **Crucial for security!** Replace the placeholder with your own unique, long, and random string. You can generate one using an online Django secret key generator or by running the following in a Python shell:
            ```python
            # from django.core.management.utils import get_random_secret_key
            # print(get_random_secret_key())
            ```
        *   `POSTGRES_DB`: Set to the name of the database you created (e.g., `library_db`).
        *   `POSTGRES_USER`: Set to the username you created (e.g., `library_user`).
        *   `POSTGRES_PASSWORD`: Set to the password for the PostgreSQL user.
        *   `POSTGRES_HOST`: Usually `localhost` if the database is on the same machine.
        *   `POSTGRES_PORT`: Usually `5432` (default PostgreSQL port).
        *   `DJANGO_DEBUG`: Set to `True` for development, `False` for production.
        *   `DJANGO_ALLOWED_HOSTS`: For development, `localhost 127.0.0.1` is fine. For production, list your actual domain(s).

6.  **Apply Database Migrations:**
    *   With the virtual environment active and `.env` configured, run:
        ```bash
        python manage.py migrate
        ```
    *   This will create the necessary tables in your PostgreSQL database based on the Django models.

7.  **Create a Superuser:**
    *   To access the Django admin panel, you need a superuser account:
        ```bash
        python manage.py createsuperuser
        ```
    *   Follow the prompts to set a username, email (optional), and password.

## Running the Application

1.  **Activate Virtual Environment (if not already active):**
    *   On macOS and Linux: `source venv/bin/activate`
    *   On Windows: `.\venv\Scripts\activate`

2.  **Start the Django Development Server:**
    ```bash
    python manage.py runserver
    ```
    *   By default, this runs the server on `http://127.0.0.1:8000/`.
    *   You can specify a different port: `python manage.py runserver 8001`.

3.  **Access the Application:**
    *   **Admin Panel:** `http://127.0.0.1:8000/admin/`
        *   *(Optional: Add a screenshot of the admin login page here)*
            `![Admin Login Page](assets/images/admin_login_example.png)`
        *   *(Optional: Add a screenshot of the admin dashboard or a model list page here)*
            `![Admin Dashboard Example](assets/images/admin_dashboard_example.png)`
    *   **API Documentation (Swagger UI):** `http://127.0.0.1:8000/swagger/`
        *   *(Optional: Add a screenshot of the Swagger UI page here)*
            `![Swagger UI Example](assets/images/swagger_ui_example.png)`
    *   **API Documentation (ReDoc):** `http://127.0.0.1:8000/redoc/`

## API Endpoints and Authentication

*   **API Base URL:** `http://127.0.0.1:8000/api/`
*   **Authentication:**
    *   Most API endpoints require JWT authentication.
    *   Obtain a JWT token by sending a POST request with your user credentials to:
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
    *   You can use the "Authorize" button in the Swagger UI to set the token for testing.

## Running Tests

*   With the virtual environment active:
    ```bash
    python manage.py test
    ```
    Or for a specific app (e.g., `core`):
    ```bash
    python manage.py test core
    ```

## Project Structure (Brief Overview)

*   `library_system/`: Main Django project directory (settings, main URLs).
*   `core/`: Django app for core functionalities (models, views, serializers, admin).
*   `requirements.txt`: Python dependencies.
*   `.env.example`: Template for environment variables. **Copy to `.env` and configure.**
*   `manage.py`: Django's command-line utility.
*   `venv/`: Python virtual environment directory (if created as per instructions, typically excluded by `.gitignore`).
*   `assets/images/`: Directory for storing static images and screenshots.
    *   `.gitkeep`: Placeholder file to ensure the directory is tracked by Git.
    *   *(You should replace `admin_login_example.png`, `admin_dashboard_example.png`, `swagger_ui_example.png` with actual screenshots after running the application.)*
*   `README.md`: This file.

---

This project is currently under development. More features and refinements will be added over time.
```
