'''
Unit tests for users.py
'''
# pylint: disable=W0621
from unittest.mock import patch
from pymongo.errors import DuplicateKeyError
import pytest
import users


@pytest.fixture
def user():
    '''
    A sample user for testing
    '''
    return ('rando', 'rando@space.star', 'random', 'star')


@pytest.fixture
def accounts():
    '''
    An empty UserCollection
    '''
    with patch('users.sql'):
        faked = users.UserCollection()
    return faked


@pytest.fixture
def dict_keys():
    '''
    Keys for database interface
    '''
    return ('user_id', 'user_email', 'user_name', 'user_last_name')


def test_user_collection_init(dict_keys):
    '''
    Test creation of UserCollection
    '''
    # pylint: disable=E1101
    with patch('users.sql') as mocker:
        result = users.UserCollection()
        assert isinstance(result, users.UserCollection)
        assert result.db_conn == mocker.DBConnection.return_value
        (result.db_conn.social['UserTable']
                       .create_index
                       .called_with(dict_keys[0], unique=True))


def test_add_user(user, accounts, dict_keys):
    '''
    Test that add_user calls database correctly
    '''
    user_create = dict(zip(dict_keys, user))
    with patch('users.sql'):
        assert accounts.add_user(*user)
        accounts.table.insert_one.assert_called_with(user_create)


def test_add_user_already_exists(user, accounts):
    '''
    Test that add_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.insert_one.side_effect = DuplicateKeyError("ERR_MSG")
        assert not accounts.add_user(*user)


def test_add_user_not_meet_restrictions(user, accounts):
    '''
    Test that add_user checks restrictions
    '''
    assert not accounts.add_user('#' * 30, *user[1:])


def test_modify_user(user, accounts, dict_keys):
    '''
    Test that modify_user calls the database correctly
    '''
    user_update = dict(zip(dict_keys, user))
    with patch('users.sql'):
        edit = {dict_keys[0]: user[0]}
        accounts.table.find_one.return_value = edit
        assert accounts.modify_user(*user)
        accounts.table.find_one.assert_called_with({dict_keys[0]: user[0]})
        accounts.table.update_one.assert_called_with({dict_keys[0]: user[0]},
                                                     {'$set': user_update})


def test_modify_user_dne(user, accounts):
    '''
    Test that modify_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.find_one.return_value = None
        assert not accounts.modify_user(*user)


def test_modify_user_not_meet_restrictions(user, accounts):
    '''
    Test that modify_user checks restrictions
    '''
    assert not accounts.modify_user('#' * 30, *user[1:])


def test_delete_user(user, accounts, dict_keys):
    '''
    Test that delete_user calls the database correctly
    '''
    with patch('users.sql'):
        assert accounts.delete_user(user[0])
        accounts.table.delete_one.assert_called_with({dict_keys[0]: user[0]})


def test_delete_user_dne(user, accounts):
    '''
    Test that delete_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.find_one.return_value = None
        assert not accounts.delete_user(user[0])


def test_search_user(user, accounts, dict_keys):
    '''
    Test that search_user calls the database correctly
    '''
    with patch('users.sql'):
        search = dict(zip(dict_keys, user))
        accounts.table.find_one.return_value = search
        result = accounts.search_user(user[0])
        accounts.table.find_one.assert_called_with({dict_keys[0]: user[0]})
    assert result == search


def test_search_user_dne(user, accounts, dict_keys):
    '''
    Test that search_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.find_one.return_value = None
        result = accounts.search_user(user[0])
    assert result == dict(zip(dict_keys, (None, None, None, None)))


def test_meet_restrictions(user, accounts):
    '''
    Test that meet_restrictions detects errors correctly
    '''
    assert accounts.meet_restrictions(user[0], *user[2:])
    assert not accounts.meet_restrictions('#' * 30, *user[2:])
    assert not accounts.meet_restrictions(user[0], '#' * 30, user[3])
    assert not accounts.meet_restrictions(user[0], user[2], '#' * 100)
