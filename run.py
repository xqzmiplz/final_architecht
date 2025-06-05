from app import create_app, db
from app.models import Task
import time
from sqlalchemy.exc import OperationalError

app = create_app()


with app.app_context():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
            break
        except OperationalError as e:
            if attempt < max_retries - 1:
                app.logger.warning(f"Database connection failed ({attempt+1}/{max_retries}), retrying...")
                time.sleep(2)
                continue
            app.logger.error("Failed to connect to database after multiple attempts")
            raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)