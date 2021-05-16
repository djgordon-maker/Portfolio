'''
Functions to interface with the user and status information
in the social network project
'''
from datetime import date
import logging
import csv
from peewee import chunked
import users
import user_status

today = date.today()
LOG_FORMAT = "%(asctime)s %(filename)s:%(lineno)-3d %(levelname)s %(message)s"
FILENAME = f"log_{today.strftime('%m_%d_%Y')}.log"
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT)
file_handler = logging.FileHandler(FILENAME)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def init_user_collection():
    '''
    Creates and returns a new instance
    of UserCollection
    '''
    logger.info('Creating a new UserCollection')
    return users.UserCollection()


def init_status_collection():
    '''
    Creates and returns a new instance
    of UserStatusCollection
    '''
    logger.info('Createing a new UserStatusCollection')
    return user_status.UserStatusCollection()


def load_users(filename, user_collection):
    '''
    Opens a CSV file with user data and
    adds it to an existing instance of
    UserCollection

    Requirements:
    - If a user_id already exists, it
    will ignore it and continue to the
    next.
    - Returns False if there are any errors
    (such as empty fields in the source CSV file)
    - Otherwise, it returns True.
    '''
    logger.debug('Entering load_users(%s, %s)', filename, user_collection)
    db_fields = ('user_id', 'user_name', 'user_last_name', 'user_email')
    user_data = []
    user_ids = set()
    if not filename.endswith('.csv'):
        logger.error('User files must be in csv format')
        return False
    with open(filename, newline='') as userfile:
        logger.info('Loading users from %s', filename)
        data = csv.reader(userfile)
        try:
            next(data)  # Eat header data
        except StopIteration:
            logger.error('%s does not contain data', filename)
            return False
        for row in data:
            # There should be four parameters
            if len(row) != 4:
                logger.error('Users need four parameters')
                return False
            # Empty strings, 0, and None are all considered empty fields
            for item in row:
                if not item:
                    logger.error('Users can not have empty fields')
                    return False
            # Filter for duplicate user_ids
            if row[0] not in user_ids:
                # Should only be called with four non-empty parameters
                logger.debug('Adding (%s) to collection', row)
                user_data.append(row)
                user_ids.add(row[0])
    logger.info('Saving collection in database')
    User = user_collection.table  # pylint: disable=C0103
    with user_collection.database.transaction():
        for batch in chunked(user_data, 100):
            User.insert_many(batch, fields=db_fields).execute()
    logger.debug('load_users() returns true')
    return True


def load_status_updates(filename, status_collection):
    '''
    Opens a CSV file with status data and
    adds it to an existing instance of
    UserStatusCollection

    Requirements:
    - If a status_id already exists, it
    will ignore it and continue to the
    next.
    - Returns False if there are any errors
    (such as empty fields in the source CSV file)
    - Otherwise, it returns True.
    '''
    logger.debug('Entering load_status_updates(%s, %s)', filename, status_collection)
    db_fields = ('status_id', 'user_id', 'status_text')
    status_data = []
    status_ids = set()
    if not filename.endswith('.csv'):
        logger.error('UserStatus files must be in csv format')
        return False
    with open(filename, newline='') as statusfile:
        logger.info('Saving statuses to %s', filename)
        data = csv.reader(statusfile)
        try:
            next(data)  # Eat header data
        except StopIteration:
            logger.error('%s does not contain data', filename)
            return False
        for row in data:
            # There should be three parameters
            if len(row) != 3:
                logger.error('UserStatus needs three parameters')
                return False
            # Empty strings, 0, and None are all considered empty fields
            for item in row:
                if not item:
                    logger.error('UserStatus can not have empty fields')
                    return False
            # Filter for duplicate status_ids
            if row[0] not in status_ids:
                # Should only be called with three non-empty parameters
                logger.debug('Adding %s to collection', row)
                status_data.append(row)
                status_ids.add(row[0])
    logger.info('Saving collection in database')
    Status = status_collection.table  # pylint: disable=C0103
    with status_collection.database.transaction():
        for batch in chunked(status_data, 100):
            Status.insert_many(batch, fields=db_fields).execute()
    return True


def add_user(user_id, email, user_name, user_last_name, user_collection):
    '''
    Creates a new instance of User and stores it in user_collection
    (which is an instance of UserCollection)

    Requirements:
    - user_id cannot already exist in user_collection.
    - Returns False if there are any errors (for example, if
    user_collection.add_user() returns False).
    - Otherwise, it returns True.
    '''
    logger.info('Adding a new User')
    return user_collection.add_user(user_id, email, user_name, user_last_name)


def update_user(user_id, email, user_name, user_last_name, user_collection):
    '''
    Updates the values of an existing user

    Requirements:
    - Returns False if there any errors.
    - Otherwise, it returns True.
    '''
    logger.info('Updating an User')
    return user_collection.modify_user(
        user_id, email, user_name, user_last_name)


def delete_user(user_id, user_collection):
    '''
    Deletes a user from user_collection.

    Requirements:
    - Returns False if there are any errors (such as user_id not found)
    - Otherwise, it returns True.
    '''
    logger.info('Deleting an User')
    return user_collection.delete_user(user_id)


def search_user(user_id, user_collection):
    '''
    Searches for a user in user_collection
    (which is an instance of UserCollection).

    Requirements:
    - If the user is found, returns the corresponding
    User instance.
    - Otherwise, it returns None.
    '''
    logger.info('Searching for an User')
    user = user_collection.search_user(user_id)
    if user.user_id:
        return user
    return None


def add_status(user_id, status_id, status_text, status_collection):
    '''
    Creates a new instance of UserStatus and stores it in user_collection
    (which is an instance of UserStatusCollection)

    Requirements:
    - status_id cannot already exist in user_collection.
    - Returns False if there are any errors (for example, if
    user_collection.add_status() returns False).
    - Otherwise, it returns True.
    '''
    logger.info('Adding an UserStatus')
    return status_collection.add_status(status_id, user_id, status_text)


def update_status(status_id, user_id, status_text, status_collection):
    '''
    Updates the values of an existing status_id

    Requirements:
    - Returns False if there any errors.
    - Otherwise, it returns True.
    '''
    logger.info('Updating an UserStatus')
    return status_collection.modify_status(status_id, user_id, status_text)


def delete_status(status_id, status_collection):
    '''
    Deletes a status_id from user_collection.

    Requirements:
    - Returns False if there are any errors (such as status_id not found)
    - Otherwise, it returns True.
    '''
    logger.info('Deleting an UserStatus')
    return status_collection.delete_status(status_id)


def search_status(status_id, status_collection):
    '''
    Searches for a status in status_collection

    Requirements:
    - If the status is found, returns the corresponding
    UserStatus instance.
    - Otherwise, it returns None.
    '''
    logger.info('Searching for an UserStatus')
    status = status_collection.search_status(status_id)
    if status.status_id:
        return status
    return None


def search_all_status_updates(user_id, status_collection):
    '''
    Searches for all statuses posted by user_id
    '''
    logger.info('Searching for matching UserStatuses')
    query = status_collection.search_all_status_updates(user_id)
    return query


def filter_status_by_string(target_string, status_collection):
    '''
    Searches for all statuses that contain target string
    '''
    logger.info('Searching for UserStatuses matching string')
    query = status_collection.filter_status_by_string(target_string)
    return query
