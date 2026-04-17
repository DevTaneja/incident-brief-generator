# No need for duplicate initialization here since it's in app.py
from app import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)