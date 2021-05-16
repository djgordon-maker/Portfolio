'''
Integration test script for menu.py
'''
# pylint: disable=R0915
from unittest.mock import patch, Mock
import menu


selections = ('accounts.csv',  # load_users()
              'dave03', 'dave@dog.org', 'Dave', 'Scott',  # add_user()
              'dave03', 'dave@dog.org', 'Dave', 'Scott',  # add_user() error
              'dave03', 'dave@new.org', 'Dave', 'Scott',  # update_user()
              'dave02', 'dave@dog.org', 'Dave', 'Scott',  # update_user() error
              'dave03',  # search_user()
              'dave02',  # search_user() error
              'dave03',  # delete_user()
              'dave03',  # delete_user() error
              'accounts.csv',  # save_users()
              'status_updates.csv',  # load_status_updates()
              'dave03', 'dave03_01', 'Try and test it',  # add_status()
              'dave03', 'dave03_01', 'Try and test it',  # add_status() error
              'dave03', 'dave03_01', 'Test looks good',  # update_status()
              'dave03', 'dave03_02', 'Test looks good',  # update_status() error
              'dave03_01',  # search_status()
              'dave03',  # search_status() error
              'dave03_01',  # delete_status()
              'dave03_01',  # delete_status() error
              'status_updates.csv')  # save_status_updates()
responces = ('User was successfully added',  # add_user()
             'An error occurred while trying to add new user',  # add_user() error
             'User was successfully updated',  # update_user()
             'An error occurred while trying to update user',  # update_user() error
             'Last name: Scott',  # search_user()
             'ERROR: User does not exist',  # search_user() error
             'User was successfully deleted',  # delete_user()
             'An error occurred while trying to delete user',  # delete_user() error
             'New status was successfully added',  # add_status()
             'An error occurred while trying to add new status',  # add_status() error
             'Status was successfully updated',  # update_status()
             'An error occurred while trying to update status',  # update_status() error
             'Status text: Test looks good',  # search_status()
             'ERROR: Status does not exist',  # search_status() error
             'Status was successfully deleted',  # delete_status()
             'An error occurred while trying to delete status')  # delete_status() error


@patch('builtins.input')
@patch('builtins.print')
@patch('menu.main.csv.writer')
@patch('menu.main.csv.reader')
def test_menu(mocked_reader, mocked_writer, mocked_print, mocked_input):
    '''
    Integration test script for menu.py
'''
    # Setup menu for testing
    mocked_input.side_effect = selections
    mocked_writer.return_value = Mock()
    menu.user_collection = menu.main.init_user_collection()
    menu.status_collection = menu.main.init_status_collection()
    # Test Users related functions
    menu.load_users()
    mocked_reader.assert_called_once()
    menu.add_user()
    mocked_print.assert_called_with(responces[0])
    assert menu.user_collection.database['dave03'].email == selections[2]
    menu.add_user()
    mocked_print.assert_called_with(responces[1])
    menu.update_user()
    mocked_print.assert_called_with(responces[2])
    assert menu.user_collection.database['dave03'].email == selections[10]
    menu.update_user()
    mocked_print.assert_called_with(responces[3])
    menu.search_user()
    mocked_print.assert_called_with(responces[4])
    menu.search_user()
    mocked_print.assert_called_with(responces[5])
    menu.delete_user()
    mocked_print.assert_called_with(responces[6])
    assert menu.user_collection.database == dict()
    menu.delete_user()
    mocked_print.assert_called_with(responces[7])
    menu.save_users()
    mocked_writer.assert_called_once()
    mocked_writer.return_value.writerow.assert_called_once()
    # Reset mocks for UserStatus tests
    mocked_reader.reset_mock()
    mocked_writer.reset_mock()
    # Test UserStatus related functions
    menu.load_status_updates()
    mocked_reader.assert_called_once()
    menu.add_status()
    mocked_print.assert_called_with(responces[8])
    menu.add_status()
    mocked_print.assert_called_with(responces[9])
    menu.update_status()
    mocked_print.assert_called_with(responces[10])
    menu.update_status()
    mocked_print.assert_called_with(responces[11])
    menu.search_status()
    mocked_print.assert_called_with(responces[12])
    menu.search_status()
    mocked_print.assert_called_with(responces[13])
    menu.delete_status()
    mocked_print.assert_called_with(responces[14])
    menu.delete_status()
    mocked_print.assert_called_with(responces[15])
    menu.save_status()
    mocked_writer.assert_called_once()
    mocked_writer.return_value.writerow.assert_called_once()
