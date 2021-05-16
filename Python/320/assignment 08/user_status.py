'''
Methods to access user status information for the social network project
'''
import logging
from functools import partial
from peewee import IntegrityError
from socialnetwork_model import user_table
from socialnetwork_model import status_table as table


logger = logging.getLogger('main.users_status')
keys = ('status_id', 'user_id', 'status_text')
status_zip = partial(zip, keys)


def make_status(status_id, user_id, status_text):
    '''
    Creates a dictionary with status information
    '''
    return dict(status_zip((status_id, user_id, status_text)))


def add_status(status_id, user_id, status_text):
    '''
    Adds a new status to the dataset
    '''
    new_status = make_status(status_id, user_id, status_text)
    # Test for foreign key constraint
    try:
        user_table.insert(user_id=user_id)
    except IntegrityError:
        # Foreign Key exists
        try:
            table.insert(**new_status)
            logger.info('Status %s added to database', status_id)
            return True
        except IntegrityError:
            logger.error('Status %s already exists', status_id)
            return False
    logger.error('Foreign Key %s does not exist', user_id)
    user_table.delete(user_id=user_id)
    return False


def modify_status(status_id, user_id, status_text):
    '''
    Modifies an existing status
    '''
    # Test for exisiting status
    exists = table.find_one(status_id=status_id)
    if not exists:
        logger.error('Status %s does not exist', status_id)
        return False
    edit_status = make_status(status_id, user_id, status_text)
    table.update(columns=['status_id'], **edit_status)
    logger.info('Status %s sucessfully modified', status_id)
    return True


def delete_status(status_id):
    '''
    Deletes an existing status
    '''
    # Test for exisiting status
    exists = table.find_one(status_id=status_id)
    if not exists:
        logger.error('Status %s does not exist', status_id)
        return False
    table.delete(status_id=status_id)
    logger.info('Status %s sucessfully deleted', status_id)
    return True


def search_status(status_id):
    '''
    Searches for and returns a statuses data
    If no status found, reutrns an empty dictionary
    '''
    # Test for exisiting status
    status = table.find_one(status_id=status_id)
    if not status:
        logger.info('Status %s not found', status_id)
        return dict(zip(keys, (None, None, None)))
    logger.info('Status %s sucessfully found', status_id)
    return status
