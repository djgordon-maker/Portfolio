'''
Unit tests for user_status.py
'''
# pylint: disable=W0621
from unittest.mock import patch
from pymongo.errors import DuplicateKeyError
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


@pytest.fixture
def dict_keys():
    '''
    Keys for database interface
    '''
    return ('status_id', 'user_id', 'status_text')


def test_user_status_collection_init(dict_keys):
    '''
    Test creation of UserStatusCollection
    '''
    # pylint: disable=E1101
    with patch('user_status.sql') as mocker:
        result = user_status.UserStatusCollection()
        assert isinstance(result, user_status.UserStatusCollection)
        assert result.db_conn == mocker.DBConnection.return_value
        (result.db_conn.social['StatusTable']
                       .create_index
                       .called_with(dict_keys[0], unique=True))


def test_add_status(status, statuses, dict_keys):
    '''
    Test that add_status calls the database correctly
    '''
    status_create = {'status_id': status[0],
                     'user_id': status[1],
                     'status_text': status[2]}
    with patch('user_status.sql'):
        user_table = statuses.db_conn.social['UserTable']
        user_table.find_one.return_value = {dict_keys[1]: status[1]}
        assert statuses.add_status(*status)
        statuses.table.insert_one.assert_called_with(status_create)


def test_add_status_already_exists(status, statuses):
    '''
    Test duplication detection for add_status
    '''
    with patch('user_status.sql'):
        statuses.table.insert_one.side_effect = DuplicateKeyError("ERR_MSG")
        assert not statuses.add_status(*status)


def test_add_status_user_dne(status, statuses, dict_keys):
    '''
    Test Forgein Key detection for add_status
    '''
    with patch('user_status.sql'):
        user_table = statuses.db_conn.__enter__().social['UserTable']
        user_table.find_one.return_value = None
        assert not statuses.add_status(*status)
        user_table.find_one.assert_called_with({dict_keys[1]: status[1]})


def test_modify_status(status, statuses, dict_keys):
    '''
    Test that modify_status calls the database correctly
    '''
    status_update = dict(zip(dict_keys, status))
    with patch('user_status.sql'):
        edit = {dict_keys[0]: status[0]}
        statuses.table.find_one.return_value = edit
        assert statuses.modify_status(*status)
        statuses.table.find_one.assert_called_with({dict_keys[0]: status[0]})
        (statuses.table.update_one.assert_called_with({dict_keys[0]: status[0]},
                                                      {'$set': status_update}))


def test_modify_status_dne(status, statuses):
    '''
    Test error detection for modify_status
    '''
    with patch('user_status.sql'):
        statuses.table.find_one.return_value = None
        assert not statuses.modify_status(*status)


def test_delete_status(status, statuses):
    '''
    Test that delete_status calls the database correctly
    '''
    with patch('user_status.sql'):
        assert statuses.delete_status(status[0])
        statuses.table.delete_one.assert_called_with({'status_id': status[0]})


def test_delete_status_dne(status, statuses):
    '''
    Test error detection for delete_status
    '''
    with patch('user_status.sql'):
        statuses.table.delete_one.return_value.deleted_count = 0
        assert not statuses.delete_status(status[0])


def test_search_status(status, statuses, dict_keys):
    '''
    Test that search_status calls the database correctly
    '''
    with patch('user_status.sql'):
        search = dict(zip(dict_keys, status))
        statuses.table.find_one.return_value = search
        result = statuses.search_status(status[0])
        statuses.table.find_one.assert_called_with({dict_keys[0]: status[0]})
    assert result is search


def test_search_status_dne(status, statuses, dict_keys):
    '''
    Test error detection for search_status
    '''
    with patch('user_status.sql'):
        statuses.table.find_one.return_value = None
        result = statuses.search_status(status[0])
        assert result == dict(zip(dict_keys, (None, None, None)))


def test_search_all_status_updates(status, statuses):
    '''
    Test that search_all_status_updates calls the database correctly
    '''
    with patch('user_status.sql'):
        result = statuses.search_all_status_updates(status[1])
        find = statuses.table.find
        count = statuses.table.count_documents
        find.assert_called_with({'user_id': status[1]})
        assert result[0] is count.return_value
        assert result[1] is find.return_value


def test_filter_status_by_string(statuses):
    '''
    Test that filter_status_by_string calls the database correctly
    '''
    target_string = "best"
    with patch('user_status.sql'):
        result = statuses.filter_status_by_string(target_string)
        statuses.table.find.assert_called_with({'$text': {'$search': target_string}})
        assert result is statuses.table.find.return_value
