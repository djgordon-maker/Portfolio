'''
Provides a clean connection to MongoDB
'''
from pymongo import MongoClient

USER_TABLE = 'UserTable'
STATUS_TABLE = 'StatusTable'


class DBConnection():
    '''
    Initialises database and provides a context manager
    '''

    def __init__(self, host='127.0.0.1', port=27017):
        '''
        Initialize database
        '''
        self.host = host
        self.port = port
        self.connection = None

    def __enter__(self):
        self.connection = MongoClient(self.host, self.port)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
