import os
import subprocess
import sys

def deploy():
    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    # Copy appropriate .env file
    if env == "production":
        os.system('copy backend\\.env.production backend\\.env')
    else:
        os.system('copy backend\\.env.development backend\\.env')
    
    # Install dependencies
    os.system('cd backend && pip install -r requirements.txt')
    
    # Run migrations
    os.system('cd backend && alembic upgrade head')
    
    # Create admin user if needed
    os.system('cd backend && python scripts/create_admin.py')
    
    if env == "development":
        os.system('cd backend && uvicorn app.main:app --reload')
    else:
        print("✅ Ready for production deployment!")
        print("Push your changes to GitHub and Render will automatically deploy")

if __name__ == "__main__":
    deploy()