# credit_service.py
import sqlite3
import logging
from fastapi import FastAPI, HTTPException, Header
from contextlib import contextmanager
import uvicorn

# --- Configuration ---
DB_PATH = ":memory:" # Use an in-memory DB for this simple example
STARTING_CREDITS = 5

app = FastAPI(title="Credit Service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Setup ---
# The database connection will be created once when the app starts.
db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)

def setup_database(conn):
    """Create and seed the database table."""
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        credits INTEGER NOT NULL
    );
    """
    )
    # Seed initial users with credits (add more users as needed)
    initial_users = ['avy', 'vaibhav']
    for user in initial_users:
        cursor.execute("INSERT OR IGNORE INTO users (username, credits) VALUES (?, ?)", (user, STARTING_CREDITS))
    conn.commit()
    logger.info("Database initialized and seeded.")

@contextmanager
def get_cursor():
    """A helper to manage database cursors."""
    cursor = db_connection.cursor()
    try:
        yield cursor
    finally:
        db_connection.commit()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/readyz")
def readyz():
    try:
        with get_cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="db not ready")

# --- API Endpoint ---
@app.post("/check")
def check_and_deduct_credits(x_consumer_username: str = Header(..., description="Username passed by Kong's key-auth plugin")):
    """
    Checks if a user has credits and deducts one.
    Returns HTTP 200 on success, HTTP 429 if out of credits.
    """
    username = x_consumer_username
    with get_cursor() as cursor:
        cursor.execute("SELECT credits FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"User '{username}' not found.")
            raise HTTPException(status_code=403, detail="User not configured for credits.")

        credits = result[0]
        if credits <= 0:
            logger.warning(f"User '{username}' has no credits remaining. Blocking request.")
            raise HTTPException(status_code=429, detail="Credit limit reached.")

        # Deduct one credit
        cursor.execute("UPDATE users SET credits = credits - 1 WHERE username = ?", (username,))
        remaining = credits - 1
        logger.info(f"User '{username}' approved. Credits remaining: {remaining}")
        return {"status": "ok", "credits_remaining": remaining}

# --- App Events ---
@app.on_event("startup")
def on_startup():
    """Setup the database when the application starts."""
    setup_database(db_connection)

@app.on_event("shutdown")
def on_shutdown():
    """Close the database connection when the application shuts down."""
    db_connection.close()
    logger.info("Database connection closed.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
