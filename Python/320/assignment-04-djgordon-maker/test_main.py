'''
Unit tests for main.py
'''
# pylint: disable=W0621
from unittest.mock import patch, Mock
import csv
import pytest
import main


@pytest.fixture
def user():
    '''
    A sample user for testing
    '''
    return ('rando', 'rando@space.star', 'random', 'star')


@pytest.fixture
def status():
    '''
    A sample status for testing
    '''
    return ('rando_001', 'rando', 'aljdfasj;')


@pytest.fixture
def user_file():
    '''
    The .csv file holding user data
    '''
    return 'accounts.csv'


@pytest.fixture
def status_file():
    '''
    The .csv file holding user data
    '''
    return 'status_updates.csv'


def test_init_user_collection():
    '''
    Test that a UserCollection is created
    '''
    with patch('main.users') as mocker:
        main.init_user_collection()
        mocker.UserCollection.assert_called_with()


def test_init_status_collection():
    '''
    Test that a UserStatusCollection is created
    '''
    with patch('main.user_status') as mocker:
        main.init_status_collection()
        mocker.UserStatusCollection.assert_called_with()


def test_load_users(user_file):
    '''
    Test that user data is tranfered from the CSV file to the database
    '''
    db_fields = ('user_id', 'user_name', 'user_last_name', 'user_email')
    # Last item must have be a repeaded user_id
    user_data = [('header to be eaten'),
                 ('evmiles97', 'Eve', 'Miles', 'eve.miles@uw.edu'),
                 ('dave03', 'David', 'Yuen', 'david.yuen@gmail.com'),
                 ('evmiles97', 'Eve', 'Miles', 'eve.miles@uw.edu')]
    csv.reader = Mock(return_value=iter(user_data))
    with patch('main.users.UserCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        assert main.load_users(user_file, mocker())
        insert.assert_called_once_with(user_data[1:-1], fields=db_fields)


def test_load_users_bad_file(user_file):
    '''
    Test that load_users will only work with .csv files
    '''
    csv.reader = Mock(return_value=iter([]))
    with patch('main.users.UserCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        assert not main.load_users(user_file[:-4], mocker())
        insert.assert_not_called()


def test_load_users_param_check(user_file):
    '''
    Test that load_users will only transfer data with four parameters
    '''
    bad_data = [('way', 'too', 'many', 'params', 'test'),
                ('missing1@info.bk', 'one', 'name'),
                ('missing2', 'two', 'name'),
                ('missing3', 'missing3@info.bk', 'name'),
                ('missing4', 'missing4@info.bk', 'four')]
    header = 'header to be eaten'
    with patch('main.users.UserCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        for test in bad_data:
            user_data = [header] + [test]
            csv.reader = Mock(return_value=iter(user_data))
            assert not main.load_users(user_file, mocker())
        insert.assert_not_called()


def test_load_users_empty_data(user_file):
    '''
    Test that load_users will not transfer empty data
    '''
    bad_data = [('', 'missing1@info.bk', 'one', 'name'),
                ('missing2', '', 'two', 'name'),
                ('missing3', 'missing3@info.bk', '', 'name'),
                ('missing4', 'missing4@info.bk', 'four', '')]
    header = 'header to be eaten'
    with patch('main.users.UserCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        for test in bad_data:
            user_data = [header] + [test]
            csv.reader = Mock(return_value=iter(user_data))
            assert not main.load_users(user_file, mocker())
        insert.assert_not_called()


def test_load_status_updates(status_file):
    '''
    Test that status data is tranfered from the CSV file to the database
    '''
    db_fields = ('status_id', 'user_id', 'status_text')
    # Last item must have be a repeaded user_id
    status_data = [('header to be eaten'),
                   ('evmiles97_00001', 'evmiles97', 'Compiling'),
                   ('dave03_00001', 'dave03', 'Sunny in Seattle'),
                   ('evmiles97_00002', 'evmiles97', 'Hike'),
                   ('dave03_00001', 'dave03', 'Sunny in Seattle')]
    csv.reader = Mock(return_value=iter(status_data))
    with patch('main.user_status.UserStatusCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        assert main.load_status_updates(status_file, mocker())
        insert.assert_called_once_with(status_data[1:-1], fields=db_fields)


def test_load_status_updates_bad_file(status_file):
    '''
    Test that load_status_updates will only work with .csv files
    '''
    csv.reader = Mock(return_value=iter([]))
    with patch('main.user_status.UserStatusCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        assert not main.load_status_updates(status_file[:-4], mocker())
        insert.assert_not_called()


def test_load_status_updates_param_check(status_file):
    '''
    Test that load_status_updates will only transfer data with three parameters
    '''
    bad_data = [('header to be eaten'),
                ('way', 'too', 'many', 'params', 'test'),
                ('one', 'message'),
                ('missing2', 'message'),
                ('missing3', 'three')]
    header = 'header to be eaten'
    with patch('main.user_status.UserStatusCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        for test in bad_data:
            status_data = [header] + [test]
            csv.reader = Mock(return_value=iter(status_data))
            assert not main.load_status_updates(status_file, mocker())
        insert.assert_not_called()


def test_load_status_updates_empty_data(status_file):
    '''
    Test that load_status_updates will not transfer empty data
    '''
    bad_data = [('', 'one', 'message'),
                ('missing2', '', 'message'),
                ('missing3', 'three', '')]
    header = 'header to be eaten'
    with patch('main.user_status.UserStatusCollection') as mocker:
        insert = mocker.return_value.table.insert_many
        for test in bad_data:
            status_data = [header] + [test]
            csv.reader = Mock(return_value=iter(status_data))
            assert not main.load_status_updates(status_file, mocker())
        insert.assert_not_called()


def test_add_user(user):
    '''
    Test that add_user is called correctly
    '''
    with patch('main.users.UserCollection') as mocker:
        add = mocker.return_value.add_user
        result = main.add_user(*user, mocker())
        add.assert_called_with(*user)
        assert result is add.return_value


def test_update_user(user):
    '''
    Test that modify_user is called correctly
    '''
    with patch('main.users.UserCollection') as mocker:
        update = mocker.return_value.modify_user
        result = main.update_user(*user, mocker())
        update.assert_called_with(*user)
        assert result is update.return_value


def test_delete_user(user):
    '''
    Test that delete_user is called correctly
    '''
    with patch('main.users.UserCollection') as mocker:
        delete = mocker.return_value.delete_user
        result = main.delete_user(user[0], mocker())
        delete.assert_called_with(user[0])
        assert result is delete.return_value


def test_search_user(user):
    '''
    Test that search_user is called correctly
    '''
    found = Mock()
    found.user_id = user[0]
    with patch('main.users.UserCollection') as mocker:
        search = mocker.return_value.search_user
        search.return_value = found
        result = main.search_user(user[0], mocker())
        search.assert_called_with(user[0])
        assert result is found


def test_search_user_dne(user):
    '''
    Test error detection for search_user
    '''
    found = Mock()
    found.user_id = None
    with patch('main.users.UserCollection') as mocker:
        search = mocker.return_value.search_user
        search.return_value = found
        result = main.search_user(user[0], mocker())
        assert result is None


def test_add_status(status):
    '''
    Test that add_status is called correctly
    '''
    with patch('main.user_status.UserStatusCollection') as mocker:
        add = mocker.return_value.add_status
        result = main.add_status(status[1], status[0], status[2], mocker())
        add.assert_called_with(*status)
        assert result is add.return_value


def test_update_status(status):
    '''
    Test that modify_status is called correctly
    '''
    with patch('main.user_status.UserStatusCollection') as mocker:
        update = mocker.return_value.modify_status
        result = main.update_status(*status, mocker())
        update.assert_called_with(*status)
        assert result is update.return_value


def test_delete_status(status):
    '''
    Test that delete_status is called correctly
    '''
    with patch('main.user_status.UserStatusCollection') as mocker:
        delete = mocker.return_value.delete_status
        result = main.delete_status(status[0], mocker())
        delete.assert_called_with(status[0])
        assert result is delete.return_value


def test_search_status(status):
    '''
    Test that search_status is called correctly
    '''
    with patch('main.user_status.UserStatusCollection') as mocker:
        search = mocker.return_value.search_status
        result = main.search_status(status[0], mocker())
        search.assert_called_with(status[0])
        assert result is search.return_value


def test_search_status_dne(status):
    '''
    Test error detection for search_status
    '''
    found = Mock()
    found.status_id = None
    with patch('main.user_status.UserStatusCollection') as mocker:
        search = mocker.return_value.search_status
        search.return_value = found
        result = main.search_status(status[0], mocker())
        assert result is None


def test_search_all_status_updates(status):
    '''
    Test that search_all_status_updates is called correctly
    '''
    with patch('main.user_status.UserStatusCollection') as mocker:
        search = mocker.return_value.search_all_status_updates
        result = main.search_all_status_updates(status[1], mocker())
        search.assert_called_with(status[1])
        assert result is search.return_value


def test_filter_status_by_string():
    '''
    Test that filter_status_by_string is called correctly
    '''
    string = 'next best'
    with patch('main.user_status.UserStatusCollection') as mocker:
        search = mocker.return_value.filter_status_by_string
        result = main.filter_status_by_string(string, mocker())
        search.assert_called_with(string)
        assert result is search.return_value
