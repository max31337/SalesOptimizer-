How to Run the Project Locally 🚀

This guide explains how to set up and run the project on your local machine for development.

Prerequisites 📋

Make sure you have installed:

🐍 Python 3.11

📦 pip

🐘 PostgreSQL 14+ (must be installed and running)

💀 Git (optional, for cloning)

🖥️ VS Code with Live Server extension (for frontend)

1. Install PostgreSQL 🐘

If you don't have PostgreSQL installed:

Download from: https://www.postgresql.org/download/

During installation, note your:

Username (e.g., postgres)

Password (e.g., your chosen password)

Port (default: 5432)

After installing:

Ensure PostgreSQL service is running.

Then, create a new database:

# Login to psql (PostgreSQL CLI)
psql -U postgres

# Inside psql shell
CREATE DATABASE SalesOptimizerDB;
\q

2. Clone the Repository 💀

git clone https://github.com/max31337/Salesoptimizer-.git
cd SalesOptimizer-

Or download the repository manually.

3. Navigate to Backend Directory 📂

cd backend

4. Create and Activate a Virtual Environment 🧪

Inside backend/:

python -m venv venv

Activate it:

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

5. Install Backend Dependencies 📦

After activating the virtual environment:

pip install -r requirements.txt

6. Configure Environment Variables ⚙️

Edit the backend/env.development file.

Example configuration:

# Main config
ENV=development
DATABASE_URL=postgresql://postgres@localhost:5432/SalesOptimizerDB
SECRET_KEY=98a0ff3d0ab843fa60e674ddeb2e08590a9c409efeb4df26c902fe77ae587294
FRONTEND_URL=http://127.0.0.1:5500
ACCESS_TOKEN_EXPIRE_MINUTES=3

# Mailtrap SMTP Settings or your own SMTP server
SMTP_SERVER=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USERNAME=
SMTP_PASSWORD=
SYSTEM_EMAIL=system@salesoptimizer.com

7. Run Database Migrations 🛠️

Apply migrations using Alembic:

cd backend
alembic upgrade head

8. Create an Initial Admin User 👨‍💻

You must create the first admin manually:

Make sure the virtual environment is activated.

Ensure PostgreSQL is running and the database exists.

Then, run:

python scripts/create_admin.py

Note:After running, it will print out the admin's credentials!

9. Run the Backend Server 🖥️

Inside backend/, start the FastAPI server:

uvicorn main:app --reload

Your FastAPI backend will now be available at:

http://127.0.0.1:8000

You can view and interact with the API documentation through Swagger UI:

http://127.0.0.1:8000/docs

10. Run the Frontend with Live Server 🌐

The frontend is located at frontend/public/.

Steps:

Open VS Code.

Navigate to frontend/public/.

Open index.html.

Right-click and select "Open with Live Server".

The frontend should be served at:

http://127.0.0.1:5500 (or a similar port)