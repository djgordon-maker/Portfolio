'''
Classes for status information for the
social network project
'''
# pylint: disable=R0903


class UserStatus():
    '''
    Contains user status information
    '''
    def __init__(self, status_id, user_id, status_text):
        self.status_id = status_id
        self.user_id = user_id
        self.status_text = status_text


class UserStatusCollection():
    '''
    Contains a collection of UserStatus objects
    '''
    def __init__(self):
        self.database = {}

    def add_status(self, status_id, user_id, status_text):
        '''
        Adds a new status to the collection
        '''
        if status_id in self.database:
            # Rejects new status if status_id already exists
            return False
        new_status = UserStatus(status_id, user_id, status_text)
        self.database[status_id] = new_status
        return True

    def modify_status(self, status_id, user_id, status_text):
        '''
        Modifies an existing status
        '''
        if status_id not in self.database:
            # Rejects update is the status_id does not exist
            return False
        self.database[status_id].user_id = user_id
        self.database[status_id].status_text = status_text
        return True

    def delete_status(self, status_id):
        '''
        Deletes an existing status
        '''
        if status_id not in self.database:
            # Fails if status does not exist
            return False
        del self.database[status_id]
        return True

    def search_status(self, status_id):
        '''
        Searches for status data
        '''
        if status_id not in self.database:
            # Fails if the status does not exist
            return UserStatus(None, None, None)
        return self.database[status_id]
