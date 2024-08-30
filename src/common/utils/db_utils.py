from functools import wraps
from src.database.db import get_db

def db_request_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            result = await func(*args, **kwargs, db=db)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    return wrapper
