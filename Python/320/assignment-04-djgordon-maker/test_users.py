'''
Unit tests for users.py
'''
# pylint: disable=W0621
from unittest.mock import patch, Mock
from peewee import IntegrityError
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


def test_user_collection_init():
    '''
    Test creation of UserCollection
    '''
    # pylint: disable=E1101
    with patch('users.sql'):
        result = users.UserCollection()
        assert isinstance(result, users.UserCollection)
        result.database.create_tables.assert_called_with([result.table])


def test_add_user(user, accounts):
    '''
    Test that add_user calls database correctly
    '''
    user_create = {'user_id': user[0],
                   'user_email': user[1],
                   'user_name': user[2],
                   'user_last_name': user[3]}
    with patch('users.sql'):
        add = Mock()
        accounts.table.create.return_value = add
        assert accounts.add_user(*user)
        accounts.table.create.assert_called_with(**user_create)
        add.save.assert_called_with()


def test_add_user_already_exists(user, accounts):
    '''
    Test that add_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.create.side_effect = IntegrityError()
        assert not accounts.add_user(*user)


def test_modify_user(user, accounts):
    '''
    Test that modify_user calls the database correctly
    '''
    with patch('users.sql'):
        edit = Mock()
        accounts.table.get.return_value = edit
        assert accounts.modify_user(*user)
        accounts.table.get.assert_called_with(user_id=user[0])
        assert edit.user_email == user[1]
        assert edit.user_name == user[2]
        assert edit.user_last_name == user[3]
        edit.save.assert_called_with()


def test_modify_user_dne(user, accounts):
    '''
    Test that modify_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.get.side_effect = IndexError()
        assert not accounts.modify_user(*user)


def test_delete_user(user, accounts):
    '''
    Test that delete_user calls the database correctly
    '''
    with patch('users.sql'):
        delete = Mock()
        accounts.table.get.return_value = delete
        assert accounts.delete_user(user[0])
        accounts.table.get.assert_called_with(user_id=user[0])
        delete.delete_instance.assert_called_with()


def test_delete_user_dne(user, accounts):
    '''
    Test that delete_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.get.side_effect = IndexError()
        assert not accounts.delete_user(user[0])


def test_search_user(user, accounts):
    '''
    Test that search_user calls the database correctly
    '''
    with patch('users.sql'):
        search = Mock()
        accounts.table.get.return_value = search
        result = accounts.search_user(user[0])
    assert result is search


def test_search_user_dne(user, accounts):
    '''
    Test that search_user responds to errors correctly
    '''
    with patch('users.sql'):
        accounts.table.get.side_effect = IndexError()
        result = accounts.search_user(user[0])
    assert result is accounts.table.return_value
