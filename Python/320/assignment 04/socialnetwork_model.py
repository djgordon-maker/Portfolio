'''
Classes that define and setup a SQLite database using peewee
'''
# pylint: disable=R0903
import os
import peewee as pw

# Ensure we are starting with an empty database
FILE = 'socialnetwork.db'
if os.path.exists(FILE):
    os.remove(FILE)

db = pw.SqliteDatabase(FILE)


class BaseModel(pw.Model):
    '''
    Hold values that apply to all tables in socialnetwork.db
    '''
    class Meta:
        '''
        Contains Metadata
        '''
        database = db


class UserTable(BaseModel):
    '''
    Defines the schema of the Users table
    '''
    user_id = pw.CharField(primary_key=True,
                           constraints=[pw.Check('LENGTH(user_id) < 30')])
    user_name = pw.CharField(constraints=[pw.Check('LENGTH(user_name) < 30')])
    user_last_name = pw.CharField(constraints=[pw.Check('LENGTH(user_last_name) < 100')])
    user_email = pw.CharField()


class StatusTable(BaseModel):
    '''
    Defines the schema of the Status table
    '''
    status_id = pw.CharField(primary_key=True)
    user_id = pw.ForeignKeyField(UserTable, on_delete='CASCADE', null=False)
    status_text = pw.CharField()
