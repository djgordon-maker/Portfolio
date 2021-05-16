'''
Classes for user information for the
social network project
'''
# pylint: disable=R0903
import logging


class Users():
    '''
    Contains user information
    '''
    def __init__(self, user_id, email, user_name, user_last_name):
        self.user_id = user_id
        self.email = email
        self.user_name = user_name
        self.user_last_name = user_last_name
        logger = logging.getLogger('main.users')
        logger.info('User %s created', user_id)


class UserCollection():
    '''
    Contains a collection of Users objects
    '''
    def __init__(self):
        self.database = {}
        self.logger = logging.getLogger('main.userscollection')
        self.logger.info('New UserCollection instance created')

    def add_user(self, user_id, email, user_name, user_last_name):
        '''
        Adds a new user to the collection
        '''
        if user_id in self.database:
            # Rejects new status if status_id already exists
            self.logger.error('User %s already exists', user_id)
            return False
        new_user = Users(user_id, email, user_name, user_last_name)
        self.database[user_id] = new_user
        self.logger.info('User %s sucessfully added', user_id)
        return True

    def modify_user(self, user_id, email, user_name, user_last_name):
        '''
        Modifies an existing user
        '''
        if user_id not in self.database:
            self.logger.error('User %s not found in database', user_id)
            return False
        self.database[user_id].email = email
        self.database[user_id].user_name = user_name
        self.database[user_id].user_last_name = user_last_name
        self.logger.info('User %s sucessfully modified', user_id)
        return True

    def delete_user(self, user_id):
        '''
        Deletes an existing user
        '''
        if user_id not in self.database:
            self.logger.error('User %s not found in database', user_id)
            return False
        del self.database[user_id]
        self.logger.info('User %s sucessfully deleted', user_id)
        return True

    def search_user(self, user_id):
        '''
        Searches for user data
        '''
        if user_id not in self.database:
            self.logger.error('User %s not found in database', user_id)
            return Users(None, None, None, None)
        self.logger.info('User %s sucessfully found', user_id)
        return self.database[user_id]
