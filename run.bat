@echo off
IF "%1"=="prod" (
    python scripts/deploy.py production
) ELSE (
    python scripts/deploy.py development
)