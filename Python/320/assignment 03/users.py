'''
Classes for user information for the
social network project
'''
# pylint: disable=R0903
import logging
from peewee import IntegrityError, DoesNotExist
import socialnetwork_model as sql


class UserCollection():
    '''
    Interfaces with the User table
    '''
    def __init__(self):
        self.table = sql.User
        self.database = sql.db
        self.database.create_tables([self.table])
        self.logger = logging.getLogger('main.userscollection')
        self.logger.info('New UserCollection instance created')

    def add_user(self, user_id, email, user_name, user_last_name):
        '''
        Adds a new user to the collection
        '''
        try:
            with sql.db.transaction():
                new_user = self.table.create(
                    user_id = user_id,
                    user_name = user_name,
                    user_last_name = user_last_name,
                    user_email = email)
                new_user.save()
        except IntegrityError as err:
            # Rejects new user if it breaks any database rules
            self.logger.error('User %s breaks database rule: %s', user_id, err)
            return False
        self.logger.info('User %s sucessfully added', user_id)
        return True

    def modify_user(self, user_id, email, user_name, user_last_name):
        '''
        Modifies an existing user
        '''
        try:
            user = self.table.get(user_id=user_id)
        except (IndexError, DoesNotExist):
            self.logger.error('User %s not found in database', user_id)
            return False
        with sql.db.transaction():
            user.user_email = email
            user.user_name = user_name
            user.user_last_name = user_last_name
            user.save()
        self.logger.info('User %s sucessfully modified', user_id)
        return True

    def delete_user(self, user_id):
        '''
        Deletes an existing user
        '''
        try:
            user = self.table.get(user_id=user_id)
        except (IndexError, DoesNotExist):
            self.logger.error('User %s not found in database', user_id)
            return False
        user.delete_instance()
        self.logger.info('User %s sucessfully deleted', user_id)
        return True

    def search_user(self, user_id):
        '''
        Searches for user data
        '''
        try:
            user = self.table.get(user_id=user_id)
        except (IndexError, DoesNotExist):
            self.logger.error('User %s not found in database', user_id)
            return self.table()
        self.logger.info('User %s sucessfully found', user.user_id)
        return user
