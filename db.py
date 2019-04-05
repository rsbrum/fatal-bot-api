import psycopg2
import logging
from flask import g
from config.config import DATABASE_CONFIG

logger = logging.getLogger('root')

def get_db():
    logger.debug("Getting database connection...")
    try:
        g.db = psycopg2.connect(dbname=DATABASE_CONFIG["dbname"], host=DATABASE_CONFIG["host"], user=DATABASE_CONFIG["user"],
                                password=DATABASE_CONFIG["password"], port=DATABASE_CONFIG["port"])

    except:
        logger.error("Database connection failed!")
        raise Exception("Database connection failed!")

    return g.db.cursor()


def close_db():
    logger.debug("Closing database connection...")
    g.db.commit()
    g.db.close()
    db = g.pop('db', None)
    if db is not None:
        db.close()

