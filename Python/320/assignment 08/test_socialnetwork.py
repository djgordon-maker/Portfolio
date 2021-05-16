'''
Unit tests for methods regaurding the social network
'''
# pylint: disable=W0621
import pytest
import users
import user_status
import main


@pytest.fixture
def user():
    '''
    Ensures that the user table is empty and returns a sample user
    '''
    users.table.delete()
    return ('rando', 'rando@new.mail', 'Rand', 'Dom')


@pytest.fixture
def status(user):
    '''
    Ensures that the user table has an user, the status table is empty,
    and returns a sample status
    '''
    user_status.table.delete()
    users.add_user(*user)
    return ('status01', user[0], 'This is text')


# Tests for users.py
def test_add_user(user):
    '''
    Test each aspect of add_user
    '''
    # Sucessfully add an user
    assert users.add_user(*user)
    # Refuse duplicate users
    assert not users.add_user(*user)
    # Refuse users breaking requirements
    assert not users.add_user('*'*31, *user[1:])
    assert not users.add_user(*user[:2], '*'*31, user[3])
    assert not users.add_user(*user[:3], '*'*101)


def test_modify_user(user):
    '''
    Test each aspect of modify_user
    '''
    # Refuse to modify non existant users
    assert not users.modify_user(*user)
    users.add_user(*user)
    # Sucessfully modify a user
    assert users.modify_user(*user)
    # Refuse users breaking requirements
    assert not users.modify_user(*user[:2], '*'*31, user[3])
    assert not users.modify_user(*user[:3], '*'*101)


def test_delete_user(user):
    '''
    Test each aspect of delete_user
    '''
    # Refuse to delete non existant users
    assert not users.delete_user(user[0])
    users.add_user(*user)
    # Sucessfully delete a user
    assert users.delete_user(user[0])


def test_search_user(user):
    '''
    Test each aspect of search_user
    '''
    # Return empty dictionary for non existant users
    data = users.search_user(user[0])
    assert data['user_id'] is None
    users.add_user(*user)
    # Sucessfully find a user
    data = users.search_user(user[0])
    assert data['user_id'] == user[0]
    assert data['user_email'] == user[1]
    assert data['user_name'] == user[2]
    assert data['user_last_name'] == user[3]


# Tests for user_status.py
def test_add_status(status):
    '''
    Test each aspect of add_status
    '''
    # Refuse statuses for non existant users
    assert not user_status.add_status(status[0], 'new_guy', status[2])
    # Sucessfully add a status
    assert user_status.add_status(*status)
    # Refuse to duplicate statuses
    assert not user_status.add_status(*status)


def test_modify_status(status):
    '''
    Test each aspect of modify_status
    '''
    # Refuse to modify a non existant status
    assert not user_status.modify_status(*status)
    user_status.add_status(*status)
    # Sucessfully modify a status
    assert user_status.modify_status(*status)


def test_delete_status(status):
    '''
    Test each aspect of delete_status
    '''
    # Refuse to delete a non existant status
    assert not user_status.delete_status(status[0])
    user_status.add_status(*status)
    # Sucessfully delete a status
    assert user_status.delete_status(status[0])


def test_search_status(status):
    '''
    Test each aspect of search_status
    '''
    # Return an empty dictionary for a non existant status
    data = user_status.search_status(status[0])
    assert data['status_id'] is None
    user_status.add_status(*status)
    # Sucessfully find a status
    data = user_status.search_status(status[0])
    assert data['status_id'] == status[0]
    assert data['user_id'] == status[1]
    assert data['status_text'] == status[2]


# Tests for main.py
def test_load_users():
    '''
    Test each aspect of load_users
    '''
    assert main.load_users('accounts.csv')


def test_load_status_updates():
    '''
    Test each aspect of load_status_updates
    '''
    assert main.load_status_updates('status_updates.csv')


def test_users_interfaces(user):
    '''
    Test functions that interface with users
    '''
    assert main.search_user(user[0]) is None
    assert main.add_user(*user)
    assert main.update_user(*user)
    assert main.search_user(user[0]) == users.search_user(user[0])
    assert main.delete_user(user[0])


def test_user_status_interfaces(status):
    '''
    Test functions that interface with user_status
    '''
    assert main.search_status(status[0]) is None
    assert main.add_status(status[1], status[0], status[2])
    assert main.update_status(*status)
    assert main.search_status(status[0]) == user_status.search_status(status[0])
    assert main.delete_status(status[0])
