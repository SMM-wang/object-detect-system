import os
from pathlib import Path

from dotenv import load_dotenv

from app import create_app


load_dotenv(Path(__file__).resolve().parent / ".env")

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host=host, port=port, debug=debug)
