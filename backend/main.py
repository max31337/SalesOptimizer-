from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",  # Ensure this path is correct
        host="127.0.0.1",
        port=8000,
        reload=True,
        workers=1,
        loop="asyncio",
        reload_delay=2
    )