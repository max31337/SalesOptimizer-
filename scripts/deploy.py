import os
import sys
from app.core.config import settings

def deploy():
    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    # Set environment
    os.environ["ENVIRONMENT"] = env
    
    # Copy appropriate .env file
    env_file = ".env.production" if env == "production" else ".env.development"
    os.system(f'copy backend\\{env_file} backend\\.env')
    
    # Install dependencies
    os.system('cd backend && pip install -r requirements.txt')
    
    # Run migrations with correct database URL
    os.system(f'cd backend && alembic upgrade head')
    
    # Create admin user if needed
    os.system('cd backend && python scripts/create_admin.py')
    
    if env == "development":
        os.system('cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000')
    else:
        print("✅ Ready for production deployment!")
        print("Push your changes to GitHub and Vercel will automatically deploy")

if __name__ == "__main__":
    deploy()