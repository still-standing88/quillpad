# QuillPad Project

A basic blog platform backend API built with Django (Django REST Framework), and a frontend SPA (built using jQuery, Bootstrap)

This is originally a University class project.


## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd quillpad # Or your project directory name
    ```

2.  **Copy Environment File:**
    Copy the example environment file and configure it for development (the defaults are usually okay for local dev):
    ```bash
    cp .env.example .env
    # Optionally edit .env if needed (e.g., different ports)
    ```

3.  **Run Setup Script:**
    This command installs frontend and backend dependencies, creates the Python virtual environment, and runs initial database migrations.
    ```bash
    npm run setup
    ```

4.  **Create Django Superuser (Optional):**
    If you want access to the Django admin interface (`/admin/`):
    ```bash
    npm run createsuperuser
    ```
    Follow the prompts to create an admin account.

5.  **Start Development Servers:**
    This command starts both the Vite frontend server (usually `http://localhost:9000`) and the Django backend server (`http://localhost:8000`) concurrently. Vite will proxy API calls.
    ```bash
    npm start
    ```
    Your browser should open automatically to the frontend URL.

## Available Scripts

-   `npm start`: Starts both frontend and backend development servers.
-   `npm run dev`: Starts only the Vite frontend dev server.
-   `npm run start:backend`: Starts only the Django backend dev server.
-   `npm run setup`: Performs initial project setup (npm install, venv, pip install, migrate).
-   `npm run build`: Creates a production-ready build of the frontend in the `dist/` folder.
-   `npm run preview`: Serves the production build locally for testing.
-   `npm run migrate`: Runs Django database migrations.
-   `npm run makemigrations`: Creates new Django migration files based on model changes.
-   `npm run createsuperuser`: Creates a Django admin user.
-   `npm run clean`: Removes generated files (`dist`, `venv`, `db.sqlite3`, migrations).

