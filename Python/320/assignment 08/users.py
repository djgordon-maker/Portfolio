'''
Methods to access user information for the social network project
'''
import logging
from functools import partial
from peewee import IntegrityError
from socialnetwork_model import user_table as table
from socialnetwork_model import status_table


logger = logging.getLogger('main.users')
keys = ('user_id', 'user_email', 'user_name', 'user_last_name')
user_zip = partial(zip, keys)


def make_user(user_id, email, user_name, user_last_name):
    '''
    Creates a dictionary with a users information
    Varifies that information meets requirements
    '''
    if len(user_id) > 30:
        logger.debug('user_id [%s] cannot be longer than 30 characters', user_id)
        return None
    if len(user_name) > 30:
        logger.debug('user_name [%s] cannot be longer than 30 characters', user_name)
        return None
    if len(user_last_name) > 100:
        logger.debug('user_last_name [%s] cannot be longer that 100 characters', user_last_name)
        return None
    return dict(user_zip((user_id, email, user_name, user_last_name)))


def add_user(user_id, email, user_name, user_last_name):
    '''
    Adds a new user to the dataset
    '''
    new_user = make_user(user_id, email, user_name, user_last_name)
    if not new_user:
        logger.error('User %s did not meet requirements', user_id)
        return False
    try:
        table.insert(**new_user)
    except IntegrityError:
        logger.error('User %s already exists', user_id)
        return False
    logger.info('User %s sucessfuly added', user_id)
    return True


def modify_user(user_id, email, user_name, user_last_name):
    '''
    Modifes an existing user
    '''
    exists = table.find_one(user_id=user_id)
    if not exists:
        logger.error('User %s does not exist', user_id)
        return False
    edit_user = make_user(user_id, email, user_name, user_last_name)
    if not edit_user:
        logger.error('User %s did not meet requirements', user_id)
        return False
    table.update(columns=['user_id'], **edit_user)
    logger.info('User %s sucessfuly modified', user_id)
    return True


def delete_user(user_id):
    '''
    Deletes an existing user
    '''
    exists = table.find_one(user_id=user_id)
    if not exists:
        logger.error('User %s does not exist', user_id)
        return False
    table.delete(user_id=user_id)
    # Delete any statuses belonging to the deleted user
    status_table.delete(user_id=user_id)
    logger.info('User %s sucessfuly deleted', user_id)
    return True


def search_user(user_id):
    '''
    Searches for user data
    Returns an empty dictionary if user is not found
    '''
    user = table.find_one(user_id=user_id)
    if not user:
        logger.info('User %s not found', user_id)
        return dict(zip(keys, (None, None, None, None)))
    logger.info('User %s sucessfuly found', user_id)
    return user
