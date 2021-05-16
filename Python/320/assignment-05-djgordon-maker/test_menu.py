'''
Integration test script for menu.py
'''
# pylint: disable=R0915
from unittest.mock import patch
import menu
import db_connection as sql


selections = ('accounts.csv',                             # load_users()
              # Test Users related functions
              'dave03', 'dave@dog.org', 'Dave', 'Scott',  # add_user()
              'dave03', 'dave@dog.org', 'Dave', 'Scott',  # add_user() error
              'dave03', 'dave@new.org', 'Dave', 'Scott',  # update_user()
              'dave02', 'dave@dog.org', 'Dave', 'Scott',  # update_user() error
              'dave03',                                   # search_user()
              'dave02',                                   # search_user() error
              'dave03',                                   # delete_user()
              'dave03',                                   # delete_user() error
              # Test UserStatus related functions
              'dave03', 'dave@dog.org', 'Dave', 'Scott',  # add_user()
              'status_updates.csv',                       # load_status_updates()
              'dave03', 'dave03_01', 'Try and test it',   # add_status()
              'dave03', 'dave03_01', 'Try and test it',   # add_status() error
              'dave03', 'dave03_01', 'Test looks good',   # update_status()
              'dave03', 'dave03_02', 'Test looks good',   # update_status() error
              'dave03_01',                                # search_status()
              'dave03',                                   # search_status() error
              'dave03_01',                                # delete_status()
              'dave03_01',                                # delete_status() error)
              # Test cascading deletes
              'dave03', 'dave03_01', 'Try and test it',   # add_status()
              'dave03',                                   # delete_user()
              'dave03_01',                                # search_status() error
              # Test table restrictions
              '#' * 30, 'id', 'too', 'long',                # add_user() error
              'name', 'too', '#' * 30, 'long',              # add_user() error
              'last_name', 'too', 'long', '#' * 100)        # add_user() error
# Test Users related functions
responces = ('User was successfully added',                       # add_user()
             'An error occurred while trying to add new user',    # add_user() error
             'User was successfully updated',                     # update_user()
             'An error occurred while trying to update user',     # update_user() error
             'Last name: Scott',                                  # search_user()
             'An error coccured while trying to find user',       # search_user() error
             'User was successfully deleted',                     # delete_user()
             'An error occurred while trying to delete user',     # delete_user() error
             # Test UserStatus related functions
             'User was successfully added',                       # add_user()
             'New status was successfully added',                 # add_status()
             'An error occurred while trying to add new status',  # add_status() error
             'Status was successfully updated',                   # update_status()
             'An error occurred while trying to update status',   # update_status() error
             'Status text: Test looks good',                      # search_status()
             'An error occurred while tryihg to find status',     # search_status() error
             'Status was successfully deleted',                   # delete_status()
             'An error occurred while trying to delete status',   # delete_status() error
             # Test cascading deletes
             'New status was successfully added',                 # add_status()
             'User was successfully deleted',                     # delete_user()
             'An error occurred while tryihg to find status',     # search_status() error
             # Test table restrictions
             'An error occurred while trying to add new user',    # add_user() error
             'An error occurred while trying to add new user',    # add_user() error
             'An error occurred while trying to add new user')    # add_user() error


@patch('builtins.input')
@patch('builtins.print')
def test_menu(mocked_print, mocked_input):
    '''
    Integration test script for menu.py
    '''
    # Drop tables for clean testing
    db_conn = sql.DBConnection()
    with db_conn as conn:
        conn.social.UserTable.drop()
        conn.social.StatusTable.drop()
    # Setup menu for testing
    mocked_input.side_effect = selections
    menu.user_collection = menu.main.init_user_collection()
    menu.status_collection = menu.main.init_status_collection()
    # Test Users related functions
    menu.load_users()
    menu.add_user()
    mocked_print.assert_called_with(responces[0])  # add_user()
    menu.add_user()
    mocked_print.assert_called_with(responces[1])  # add_user() error
    menu.update_user()
    mocked_print.assert_called_with(responces[2])  # update_user()
    menu.update_user()
    mocked_print.assert_called_with(responces[3])  # update_user() error
    menu.search_user()
    mocked_print.assert_called_with(responces[4])  # search_user()
    menu.search_user()
    mocked_print.assert_called_with(responces[5])  # search_user() error
    menu.delete_user()
    mocked_print.assert_called_with(responces[6])  # delete_user()
    menu.delete_user()
    mocked_print.assert_called_with(responces[7])  # delete_user() error
    # Test UserStatus related functions
    menu.add_user()
    mocked_print.assert_called_with(responces[8])  # add_user() for status
    menu.load_status_updates()
    menu.add_status()
    mocked_print.assert_called_with(responces[9])  # add_status()
    menu.add_status()
    mocked_print.assert_called_with(responces[10])  # add_status() error
    menu.update_status()
    mocked_print.assert_called_with(responces[11])  # update_status()
    menu.update_status()
    mocked_print.assert_called_with(responces[12])  # update_status() error
    menu.search_status()
    mocked_print.assert_called_with(responces[13])  # search_status()
    menu.search_status()
    mocked_print.assert_called_with(responces[14])  # search_status() error
    menu.delete_status()
    mocked_print.assert_called_with(responces[15])  # delete_status()
    menu.delete_status()
    mocked_print.assert_called_with(responces[16])  # delete_status() error
    # Test cascading deletes
    menu.add_status()
    mocked_print.assert_called_with(responces[17])  # add_status()
    menu.delete_user()
    mocked_print.assert_called_with(responces[18])  # delete_user()
    menu.search_status()
    mocked_print.assert_called_with(responces[19])  # search_status() error
    # Test table restrictions
    menu.add_user()
    mocked_print.assert_called_with(responces[20])  # add_user() error
    menu.add_user()
    mocked_print.assert_called_with(responces[21])  # add_user() error
    menu.add_user()
    mocked_print.assert_called_with(responces[22])  # add_user() error
