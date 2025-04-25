# QuillPad Project

A blog platform backend API built with Django & Django REST Framework, and a frontend SPA built using Vite, jQuery, and Bootstrap 5.

## Project Structure

-   `.`: Root directory (contains config files, `manage.py` launcher for backend).
    -   `requirements.txt`: Python backend dependencies.
    -   `package.json`: Node.js frontend dependencies and scripts.
    -   `vite.config.js`: Vite build tool configuration.
    -   `.env.example`: Template for environment variables. **Copy to `.env` and configure.**
    -   `.gitignore`: Specifies intentionally untracked files.
    -   `README.md`: This file.
    -   `.vscode/`: Optional VS Code settings and extension recommendations.
    -   `venv/`: Python virtual environment (created by setup).
    -   `node_modules/`: Node.js packages (created by setup).
    -   `dist/`: Production frontend build output (created by `npm run build`).
-   `src/`: Contains the source code.
    -   `api/`: Django backend application source.
        -   `blog/`: Blog app (models, views, serializers for posts, comments, etc.).
        -   `users/`: Custom user model app.
        -   `quillpad_backend/`: Django project settings, WSGI entry point.
        -   `manage.py`: Django management script.
        -   `db.sqlite3`: Development SQLite database (created by setup).
        -   `mediafiles/`: User uploaded media (created on first upload, configure path in settings).
    -   `css/`: Frontend CSS files.
        -   `style.css`: Custom application styles.
    -   `js/`: Frontend JavaScript files (ES Modules).
        -   `core/`: Core modules (api, auth, init).
        -   `handlers/`: Event handler logic.
        -   `ui/`: UI rendering functions.
        -   `router.js`: Hash-based SPA routing logic.
        -   `main.js`: Vite entry point, imports CSS and JS modules.
    -   `index.html`: Main HTML entry point for the frontend SPA.

## Prerequisites

-   Python 3.8+
-   Node.js 18+ and npm

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

## Production Deployment Outline

Deploying this requires setting up a server environment. Here's a high-level overview:

1.  **Server Setup:** Provision a server (e.g., Linux VPS). Install Python, Node.js, npm, a database (e.g., PostgreSQL), and a web server (e.g., Nginx).
2.  **Clone Code:** Clone your repository onto the server.
3.  **Configure Environment (`.env`):**
    *   Copy `.env.example` to `.env`.
    *   **Set `DEBUG=False`**.
    *   Generate and set a strong `SECRET_KEY`.
    *   Set `ALLOWED_HOSTS` to your production domain(s).
    *   Set the `DATABASE_URL` for your production database.
    *   Set `CORS_ALLOWED_ORIGINS` to your production frontend domain(s) (e.g., `https://yourdomain.com`).
    *   Configure production `EMAIL_*` settings.
4.  **Setup Backend:**
    *   Run `npm run setup:venv` (or create venv manually).
    *   Run `npm run setup:pip` (or activate venv and `pip install -r requirements.txt`).
    *   Install Gunicorn: `pip install gunicorn` (add to `requirements.txt`).
    *   Run migrations on the production database: `npm run migrate` (or activate venv and `python src/api/manage.py migrate`).
    *   Collect Django static files: `npm run collectstatic` (or activate venv and `python src/api/manage.py collectstatic`). Ensure `STATIC_ROOT` in `settings.py` points to the correct location.
5.  **Build Frontend:**
    *   Run `npm install` (if not already done).
    *   Run `npm run build`. This creates the `dist/` directory.
6.  **Configure WSGI Server (Gunicorn):**
    *   Set up a process manager (`systemd`, `supervisor`) to run Gunicorn.
    *   Example command (using a socket):
        ```bash
        # /etc/systemd/system/gunicorn.service example
        [Unit]
        Description=gunicorn daemon for QuillPad
        After=network.target

        [Service]
        User=<your_deploy_user>
        Group=<your_deploy_group>
        WorkingDirectory=/path/to/your/project
        ExecStart=/path/to/your/project/venv/bin/gunicorn --access-logfile - \
                  --error-logfile - --workers 3 \
                  --bind unix:/path/to/your/project/gunicorn.sock \
                  src.api.quillpad_backend.wsgi:application

        [Install]
        WantedBy=multi-user.target
        ```
    *   Remember to adjust paths, user, group, and `--workers`. Enable and start the service.
7.  **Configure Web Server (Nginx):**
    *   Install Nginx.
    *   Create an Nginx server block configuration file (e.g., in `/etc/nginx/sites-available/`).
    *   Configure it to:
        *   Serve static frontend files from the `dist/` directory.
        *   Serve Django static files from the `STATIC_ROOT` directory (e.g., `/static/`).
        *   Serve media files from the `MEDIA_ROOT` directory (e.g., `/media/`).
        *   Proxy requests to `/api/`, `/admin/`, etc., to the Gunicorn socket or port.
        *   Handle HTTPS (using Let's Encrypt/Certbot is recommended).
    *   Enable the site and restart Nginx. (Refer to Nginx documentation for specifics).

## VS Code Extensions (Optional)

If using VS Code, the `.vscode/extensions.json` file recommends extensions for Python and web development. Open the project in VS Code, and it should prompt you to install the recommended extensions.