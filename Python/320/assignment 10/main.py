'''
Functions to interface with the user and status information
in the social network project
'''
from datetime import date
import logging
import csv
import socialnetwork_model as sql
import users
import user_status
import picture

today = date.today()
LOG_FORMAT = "%(asctime)s %(filename)s:%(lineno)-3d %(levelname)s %(message)s"
FILENAME = f"log_{today.strftime('%m_%d_%Y')}.log"
logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
formatter = logging.Formatter(LOG_FORMAT)
file_handler = logging.FileHandler(FILENAME)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_users(filename):
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
    if not filename.endswith('.csv'):
        logger.error('User files must be in csv format')
        return False
    with open(filename, newline='') as userfile:
        logger.info('Loading users from %s', filename)
        data = csv.reader(userfile)
        try:
            next(data)
        except StopIteration:
            logger.error('%s does not contain data', filename)
            return False
        for row in data:
            # Inspect csv data
            logger.debug('Inspecting %s', row)
            if len(row) != 4:
                logger.error('Users need four parameters')
                return False
            # Empty strings, 0, and None are all considered empty fields
            for item in row:
                if not item:
                    logger.error('Users can not have empty fields')
                    return False
            users.add_user(row[0], row[2], row[3], row[1])
            # If user does not meet requirements ignore and continue
    return True


def load_status_updates(filename):
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
    if not filename.endswith('.csv'):
        logger.error('Status files must be in csv format')
        return False
    # Collect user_ids to ensure forign key compliance
    user_ids = set()
    with sql.connection(sql.USER) as table:
        data = table.all()
        for row in data:
            user_ids.add(row['user_id'])
    with open(filename, newline='') as statusfile:
        logger.info('Loading status updates from %s', filename)
        data = csv.reader(statusfile)
        try:
            next(data)  # Eat header data
        except StopIteration:
            logger.error('%s does not contain data', filename)
            return False
        for row in data:
            logger.debug('Inspecting %s', row)
            # Inspect csv data
            if len(row) != 3:
                logger.error('Statuses need three parameters')
                return False
            # Empty strings, 0, and None are all considered empty fields
            for item in row:
                if not item:
                    logger.error('Statuses can not have empty fields')
                    return False
            if row[1] in user_ids:
                status = user_status.make_status(*row)
                with sql.connection(sql.STATUS) as table:
                    table.insert(**status)
                    logger.info('Status %s added to database', row[0])
                    continue  # Moves onto the next row if there are no exceptions
                # IntegrityError is the only excpetion that we catch
                logger.error('Status %s already exists', row[0])
            else:
                logger.error('User %s does not exist', row[1])
            # If status does not meet requirements ignore and continue
    return True


def add_user(user_id, email, user_name, user_last_name):
    '''
    Creates a new instance of User and stores it in the database

    Requirements:
    - user_id cannot already exist in the database
    - Returns False if there are any errors
    - Otherwise, it returns True.
    '''
    logger.info('Adding a new User')
    return users.add_user(user_id, email, user_name, user_last_name)


def update_user(user_id, email, user_name, user_last_name):
    '''
    Updates the values of an existing user

    Requirements:
    - Returns False if there any errors.
    - Otherwise, it returns True.
    '''
    logger.info('Updating an User')
    return users.modify_user(user_id, email, user_name, user_last_name)


def delete_user(user_id):
    '''
    Deletes a user from the database

    Requirements:
    - Returns False if there are any errors (such as user_id not found)
    - Otherwise, it returns True.
    '''
    logger.info('Deleting an User')
    return users.delete_user(user_id)


def search_user(user_id):
    '''
    Searches for a user in the database

    Requirements:
    - If the user is found, returns the corresponding User.
    - Otherwise, it returns None.
    '''
    logger.info('Searching for an User')
    user = users.search_user(user_id)
    if user['user_id']:
        return user
    return None


def add_status(user_id, status_id, status_text):
    '''
    Creates a new instance of UserStatus and stores it in the database

    Requirements:
    - status_id cannot already exist in the database.
    - Returns False if there are any errors
    - Otherwise, it returns True.
    '''
    logger.info('Adding a Status')
    return user_status.add_status(status_id, user_id, status_text)


def update_status(status_id, user_id, status_text):
    '''
    Updates the values of an existing status_id

    Requirements:
    - Returns False if there any errors.
    - Otherwise, it returns True.
    '''
    logger.info('Updating a Status')
    return user_status.modify_status(status_id, user_id, status_text)


def delete_status(status_id):
    '''
    Deletes a status_id from the database

    Requirements:
    - Returns False if there are any errors (such as status_id not found)
    - Otherwise, it returns True.
    '''
    logger.info('Deleting an UserStatus')
    return user_status.delete_status(status_id)


def search_status(status_id):
    '''
    Searches for a status in the database

    Requirements:
    - If the status is found, returns the corresponding Status.
    - Otherwise, it returns None.
    '''
    logger.info('Searching for an UserStatus')
    status = user_status.search_status(status_id)
    if status['status_id']:
        return status
    return None


def upload_picture(user_id, tags):
    '''
    Uploads an image onto the database
    '''
    logger.info('Uploading a picture')
    return picture.add_picture(user_id, tags)


def list_user_images(user_id):
    '''
    Lists all images owned by a user
    '''
    logger.info('Listing images')
    return picture.list_user_images(user_id)
