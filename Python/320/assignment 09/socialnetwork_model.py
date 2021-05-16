'''
Functions that create a connection to User and Status tables
Import user_table and status_table directly
'''
import logging
import os
from contextlib import contextmanager
from peewee import IntegrityError
from playhouse.dataset import DataSet
from log import logit

logger = logging.getLogger('main.sql')
logger.setLevel(logging.DEBUG)

# Ensure we are starting with an empty database
FILE = 'socialnetwork.db'
USER = 'User'
STATUS = 'Status'
PICTURE = 'Picture'

if os.path.exists(FILE):
    os.remove(FILE)

# Connect to database
SQL_URL = 'sqlite:///' + FILE
db = DataSet(SQL_URL)
# Setup User
user_table = db[USER]
user_table.insert(user_id='blank')
user_table.create_index(['user_id'], unique=True)
user_table.delete(user_id='blank')
# Setup Status
status_table = db[STATUS]
status_table.insert(status_id='blank', user_id='blank')
status_table.create_index(['status_id'], unique=True)
status_table.delete(status_id='blank')
# Setup Picture
picture_table = db[PICTURE]
picture_table.insert(picture_id='blank', user_id='blank')
picture_table.create_index(['picture_id'], unique=True)
picture_table.delete(picture_id='blank')
db.close()


@logit(logger)
@contextmanager
def connection(table):
    '''
    Context manager for connecting to the database
    Returns the table to connect to
    '''
    try:
        db.connect()
        logger.debug('%s opened', table)
        yield db[table]
    # Code curretnly assumes that we only catch IntegrityError
    # Will need more robust error handling to catch other exception types
    except IntegrityError:
        logger.error('IntegrityError detected')
        return
    finally:
        db.close()
        logger.debug('%s closed', table)


# Simple program to test connection()
if __name__ == '__main__':
    user = {'user_id': 'id', 'user_email': 'mailit',
            'user_name': 'named', 'user_last_name': 'lasterd'}
    with connection(USER) as test_table:
        print(test_table.insert(**user))
        print('inserted one')
        print(test_table.insert(**user))
        print('inserted two')
