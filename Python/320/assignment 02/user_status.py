'''
Classes for status information for the
social network project
'''
# pylint: disable=R0903
import logging


class UserStatus():
    '''
    Contains user status information
    '''
    def __init__(self, status_id, user_id, status_text):
        self.status_id = status_id
        self.user_id = user_id
        self.status_text = status_text
        logger = logging.getLogger('main.userstatus')
        logger.info('Status %s created', status_id)


class UserStatusCollection():
    '''
    Contains a collection of UserStatus objects
    '''
    def __init__(self):
        self.database = {}
        self.logger = logging.getLogger('main.userstatuscollection')
        self.logger.info('New UserStatusCollection instance created')

    def add_status(self, status_id, user_id, status_text):
        '''
        Adds a new status to the collection
        '''
        if status_id in self.database:
            # Rejects new status if status_id already exists
            self.logger.error('Status %s already in database', status_id)
            return False
        new_status = UserStatus(status_id, user_id, status_text)
        self.database[status_id] = new_status
        self.logger.info('Status %s added to database', status_id)
        return True

    def modify_status(self, status_id, user_id, status_text):
        '''
        Modifies an existing status
        '''
        if status_id not in self.database:
            # Rejects update is the status_id does not exist
            self.logger.error('Status %s not found database', status_id)
            return False
        self.database[status_id].user_id = user_id
        self.database[status_id].status_text = status_text
        self.logger.info('Status %s sucessfully modified', status_id)
        return True

    def delete_status(self, status_id):
        '''
        Deletes an existing status
        '''
        if status_id not in self.database:
            # Fails if status does not exist
            self.logger.error('Status %s not found database', status_id)
            return False
        del self.database[status_id]
        self.logger.info('Status %s sucessfully deleted', status_id)
        return True

    def search_status(self, status_id):
        '''
        Searches for status data
        '''
        if status_id not in self.database:
            # Fails if the status does not exist
            self.logger.error('Status %s not found database', status_id)
            return UserStatus(None, None, None)
        self.logger.info('Status %s sucessfully found', status_id)
        return self.database[status_id]
