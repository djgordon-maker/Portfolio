'''
Classes for user information for the
social network project
'''
# pylint: disable=R0903
import logging
from pymongo.errors import DuplicateKeyError
import db_connection as sql


MAX_ID_LENGTH = 30
MAX_NAME_LENGTH = 30
MAX_LAST_NAME_LENGTH = 100


class UserCollection():
    '''
    Interfaces with the User table
    '''
    def __init__(self):
        self.dict_keys = ('user_id', 'user_name', 'user_last_name', 'user_email')
        self.db_conn = sql.DBConnection()
        with self.db_conn as db_conn:
            self.table = db_conn.social[sql.USER_TABLE]
            self.table.create_index(self.dict_keys[0], unique=True)
        self.logger = logging.getLogger('main.userscollection')
        self.logger.info('New UserCollection instance created')

    def add_user(self, user_id, email, user_name, user_last_name):
        '''
        Adds a new user to the collection
        '''
        dict_values = (user_id, user_name, user_last_name, email)
        new_user = dict(zip(self.dict_keys, dict_values))
        if not self.meet_restrictions(user_id, user_name, user_last_name):
            # Rejects users that dont meet table restrictions
            return False
        try:
            with self.db_conn:
                self.table.insert_one(new_user)
        except DuplicateKeyError as err:
            # Rejects new user if it breaks any database rules
            self.logger.error('User %s breaks database rule: %s', user_id, err)
            return False
        self.logger.info('User %s sucessfully added', user_id)
        return True

    def modify_user(self, user_id, email, user_name, user_last_name):
        '''
        Modifies an existing user
        '''
        dict_values = (user_id, user_name, user_last_name, email)
        search_term = {self.dict_keys[0]: user_id}
        if not self.meet_restrictions(user_id, user_name, user_last_name):
            # Rejects users that dont meet table restrictions
            return False
        with self.db_conn:
            user = self.table.find_one(search_term)
            if not user:
                # Rejects edit is the user does not exist
                self.logger.error('User %s not found in database', user_id)
                return False
            user = dict(zip(self.dict_keys, dict_values))
            self.table.update_one(search_term, {'$set': user})
        self.logger.info('User %s sucessfully modified', user_id)
        return True

    def delete_user(self, user_id):
        '''
        Deletes an existing user
        Required to detect when the user is not found and return False
        '''
        search_term = {self.dict_keys[0]: user_id}
        with self.db_conn as db_conn:
            result = self.table.find_one(search_term)
            if not result:
                # Fails if nothing was deleted
                self.logger.error('User %s not found in database', user_id)
                return False
            status_table = db_conn.social[sql.STATUS_TABLE]
            status_table.delete_many(search_term)
            self.table.delete_one(search_term)
        self.logger.info('User %s sucessfully deleted', user_id)
        return True

    def search_user(self, user_id):
        '''
        Searches for user data
        Required to detect when the user is not found and return an empty user
        '''
        with self.db_conn:
            user = self.table.find_one({self.dict_keys[0]: user_id})
        if not user:
            self.logger.error('User %s not found in database', user_id)
            return dict(zip(self.dict_keys, (None, None, None, None)))
        self.logger.info('User %s sucessfully found', user_id)
        return user

    def meet_restrictions(self, user_id, user_name, user_last_name):
        '''
        Checks that users meet table restrictions
        '''
        if len(user_id) >= MAX_ID_LENGTH:
            self.logger.error('User id %s is longer than %s',
                              user_id, MAX_ID_LENGTH)
            return False
        if len(user_name) >= MAX_NAME_LENGTH:
            self.logger.error('User name %s is longer than %s',
                              user_name, MAX_NAME_LENGTH)
            return False
        if len(user_last_name) >= MAX_LAST_NAME_LENGTH:
            self.logger.error('User last name %s is longer than %s',
                              user_last_name, MAX_LAST_NAME_LENGTH)
            return False
        return True
