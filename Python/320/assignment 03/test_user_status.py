'''
Unit tests for user_status.py
'''
# pylint: disable=W0621
from unittest.mock import patch, Mock
from peewee import IntegrityError
import pytest
import user_status


@pytest.fixture
def status():
    '''
    A sample status for testing
    '''
    return ('rando_001', 'rando', 'aljdfasj;')


@pytest.fixture
def statuses():
    '''
    An empty StatusCollection
    '''
    with patch('user_status.sql'):
        faked = user_status.UserStatusCollection()
    return faked


def test_user_status_collection_init():
    '''
    Test creation of UserStatusCollection
    '''
    # pylint: disable=E1101
    with patch('user_status.sql'):
        result = user_status.UserStatusCollection()
        assert isinstance(result, user_status.UserStatusCollection)
        result.database.execute_sql.assert_called_with('PRAGMA foreign_keys = ON;')
        result.database.create_tables.assert_called_with([result.table])


def test_add_status(status, statuses):
    '''
    Test that add_status calls the database correctly
    '''
    status_create = {'status_id': status[0],
                     'user_id': status[1],
                     'status_text': status[2]}
    with patch('user_status.sql'):
        add = Mock()
        statuses.table.create.return_value = add
        assert statuses.add_status(*status)
        statuses.table.create.assert_called_with(**status_create)
        add.save.assert_called_with()


def test_add_status_already_exists(status, statuses):
    '''
    Test error detection for add_status
    '''
    with patch('user_status.sql'):
        statuses.table.create.side_effect = IntegrityError()
        assert not statuses.add_status(*status)


def test_modify_status(status, statuses):
    '''
    Test that modify_status calls the database correctly
    '''
    with patch('user_status.sql'):
        edit = Mock()
        statuses.table.get.return_value = edit
        assert statuses.modify_status(*status)
        statuses.table.get.assert_called_with(status_id=status[0])
        assert edit.user_id == status[1]
        assert edit.status_text == status[2]
        edit.save.assert_called_with()


def test_modify_status_dne(status, statuses):
    '''
    Test error detection for modify_status
    '''
    with patch('user_status.sql'):
        statuses.table.get.side_effect = IndexError()
        assert not statuses.modify_status(*status)


def test_delete_status(status, statuses):
    '''
    Test that delete_status calls the database correctly
    '''
    with patch('user_status.sql'):
        delete = Mock()
        statuses.table.get.return_value = delete
        assert statuses.delete_status(status[0])
        statuses.table.get.assert_called_with(status_id=status[0])
        delete.delete_instance.assert_called_with()


def test_delete_status_dne(status, statuses):
    '''
    Test error detection for delete_status
    '''
    with patch('user_status.sql'):
        statuses.table.get.side_effect = IndexError()
        assert not statuses.delete_status(status[0])


def test_search_status(status, statuses):
    '''
    Test that search_status calls the database correctly
    '''
    with patch('user_status.sql'):
        search = Mock()
        search.status_id = status[0]
        search.user_id = status[1]
        search.status_text = status[2]
        statuses.table.get.return_value = search
        result = statuses.search_status(status[0])
        statuses.table.get.assert_called_with(status_id=status[0])
    assert result == search


def test_search_status_dne(status, statuses):
    '''
    Test error detection for search_status
    '''
    with patch('user_status.sql'):
        statuses.table.get.side_effect = IndexError()
        result = statuses.search_status(status[0])
        assert result == statuses.table.return_value
