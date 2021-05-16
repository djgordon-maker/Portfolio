'''
Classes for status information for the
social network project
'''
# pylint: disable=R0903
import logging
from peewee import IntegrityError, DoesNotExist
import socialnetwork_model as sql


class UserStatusCollection():
    '''
    Interfaces with the Status table
    '''
    def __init__(self):
        self.table = sql.StatusTable
        self.database = sql.db
        self.database.execute_sql('PRAGMA foreign_keys = ON;')
        self.database.create_tables([self.table])
        self.logger = logging.getLogger('main.userstatuscollection')
        self.logger.info('New UserStatusCollection instance created')

    def add_status(self, status_id, user_id, status_text):
        '''
        Adds a new status to the collection
        '''
        try:
            with self.database.transaction():
                new_status = self.table.create(
                    status_id = status_id,
                    user_id = user_id,
                    status_text = status_text)
                new_status.save()
        except IntegrityError as err:
            # Rejects new status if it breaks one of the databases rules
            self.logger.error('Status %s breaks database rule: %s', status_id, err)
            return False
        self.logger.info('Status %s added to database', status_id)
        return True

    def modify_status(self, status_id, user_id, status_text):
        '''
        Modifies an existing status
        '''
        try:
            status = self.table.get(status_id=status_id)
        except (IndexError, DoesNotExist):
            # Rejects update is the status_id does not exist
            self.logger.error('Status %s not found database', status_id)
            return False
        with self.database.transaction():
            status.user_id = user_id
            status.status_text = status_text
            status.save()
        self.logger.info('Status %s sucessfully modified', status_id)
        return True

    def delete_status(self, status_id):
        '''
        Deletes an existing status
        '''
        try:
            status = self.table.get(status_id=status_id)
        except (IndexError, DoesNotExist):
            # Fails if status does not exist
            self.logger.error('Status %s not found database', status_id)
            return False
        status.delete_instance()
        self.logger.info('Status %s sucessfully deleted', status_id)
        return True

    def search_status(self, status_id):
        '''
        Searches for status data
        '''
        try:
            status = self.table.get(status_id=status_id)
        except (IndexError, DoesNotExist):
            # Fails if the status does not exist
            self.logger.error('Status %s not found database', status_id)
            return self.table()
        self.logger.info('Status %s sucessfully found', status_id)
        return status

    def search_all_status_updates(self, user_id):
        '''
        Searches for all statuses posted by user_id
        '''
        query = self.table.select().where(self.table.user_id == user_id)
        self.logger.info('Found statuses posted by %s', user_id)
        return query

    def filter_status_by_string(self, target):
        '''
        Searches for all statuses that contain target string
        '''
        query = (self.table.select()
                 .where(self.table.status_text.contains(target))
                 .iterator())
        self.logger.info('Found statuses matching %s', target)
        return query
