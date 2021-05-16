'''
Functions that create a connection to User and Status tables
Import user_table and status_table directly
'''
import os
from playhouse.dataset import DataSet

# Ensure we are starting with an empty database
FILE = 'socialnetwork.db'
if os.path.exists(FILE):
    os.remove(FILE)

# Connect to database
SQL_URL = 'sqlite:///' + FILE
db = DataSet(SQL_URL)
# Setup User
user_table = db['User']
user_table.insert(user_id='blank')
user_table.create_index(['user_id'], unique=True)
user_table.delete(user_id='blank')
# Setup Status
status_table = db['Status']
status_table.insert(status_id='blank', user_id='blank')
status_table.create_index(['status_id'], unique=True)
status_table.delete(status_id='blank')
