'''
Classes for status information for the
social network project
'''
# pylint: disable=R0903
import logging
from pymongo.errors import DuplicateKeyError
import db_connection as sql


class UserStatusCollection():
    '''
    Interfaces with the Status table
    '''
    def __init__(self):
        self.dict_keys = ('status_id', 'user_id', 'status_text')
        self.db_conn = sql.DBConnection()
        with self.db_conn as db_conn:
            self.table = db_conn.social[sql.STATUS_TABLE]
            self.table.create_index('status_id', unique=True)
            self.table.create_index([('status_text', 'text')])
        self.logger = logging.getLogger('main.userstatuscollection')
        self.logger.info('New UserStatusCollection instance created')

    def add_status(self, status_id, user_id, status_text):
        '''
        Adds a new status to the collection
        '''
        dict_values = (status_id, user_id, status_text)
        new_status = dict(zip(self.dict_keys, dict_values))
        try:
            with self.db_conn as db_conn:
                user_table = db_conn.social[sql.USER_TABLE]
                if user_table.find_one({self.dict_keys[1]: user_id}):
                    # Insure user already exists
                    self.table.insert_one(new_status)
                else:
                    # Reject posts without a user
                    self.logger.error('User %s does not exist', user_id)
                    return False
        except DuplicateKeyError:
            # Rejects new status if status_id already exists
            self.logger.error('Status %s already exists in database', status_id)
            return False
        self.logger.info('Status %s added to database', status_id)
        return True

    def modify_status(self, status_id, user_id, status_text):
        '''
        Modifies an existing status
        '''
        search_term = {self.dict_keys[0]: status_id}
        with self.db_conn:
            status = self.table.find_one(search_term)
            if not status:
                # Rejects edit is the status does not exist
                self.logger.error('Status %s not found database', status_id)
                return False
            status[self.dict_keys[1]] = user_id
            status[self.dict_keys[2]] = status_text
            self.table.update_one(search_term, {'$set': status})
        self.logger.info('Status %s sucessfully modified', status_id)
        return True

    def delete_status(self, status_id):
        '''
        Deletes an existing status
        Required to detect when the status is not found and return False
        '''
        with self.db_conn:
            result = self.table.delete_one({self.dict_keys[0]: status_id})
            if result.deleted_count == 0:
                # Fails if nothing was deleted
                self.logger.error('Status %s not found database', status_id)
                return False
        self.logger.info('Status %s sucessfully deleted', status_id)
        return True

    def search_status(self, status_id):
        '''
        Searches for status data
        Required to detect when the status is not found and return an empty status
        '''
        with self.db_conn:
            status = self.table.find_one({self.dict_keys[0]: status_id})
        if not status:
            # Fails if the status does not exist
            self.logger.error('Status %s not found database', status_id)
            return dict(zip(self.dict_keys, (None, None, None)))
        self.logger.info('Status %s sucessfully found', status_id)
        return status

    def search_all_status_updates(self, user_id):
        '''
        Searches for all statuses posted by user_id
        '''
        query = self.table.find({self.dict_keys[1]: user_id})
        count = self.table.count_documents({self.dict_keys[1]: user_id})
        self.logger.info('Found statuses posted by %s', user_id)
        return (count, query)

    def filter_status_by_string(self, target):
        '''
        Searches for all statuses that contain target string
        '''
        query = self.table.find({'$text': {'$search': target}})
        self.logger.info('Found statuses matching %s', target)
        return query
