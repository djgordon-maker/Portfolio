'''
Unit tests for methods regaurding the social network
'''
# pylint: disable=W0621
from pathlib import Path
from unittest.mock import Mock
import csv
import pytest
from pytest import MonkeyPatch  # pylint: disable=W0611
import users
import user_status
import picture
import main
import socialnetwork_model as sql


@pytest.fixture
def user():
    '''
    Ensures that the user table is empty and returns a sample user
    '''
    with sql.connection(sql.USER) as table:
        table.delete()
    return ('rando', 'rando@new.mail', 'Rand', 'Dom')


@pytest.fixture
def status(user):
    '''
    Ensures that the user table has an user, the status table is empty,
    and returns a sample status
    '''
    with sql.connection(sql.STATUS) as table:
        table.delete()
    users.add_user(*user)
    return ('status01', user[0], 'This is text')


@pytest.fixture
def pic(user):
    '''
    Ensures that the user table has an user, the picture table is empty,
    the users image directory is deleted, and returns a sample picture
    '''
    with sql.connection(sql.PICTURE) as table:
        table.delete()
    clear_dir(Path(user[0]))
    users.add_user(*user)
    return (user[0], '#car #bmw #sTronG_EMOtiON')


def clear_dir(path):
    '''
    Deletes image directory of given user
    '''
    if not path.is_dir():
        return
    for tag in path.iterdir():
        if tag.is_file():
            tag.unlink()
        else:
            clear_dir(tag)
    path.rmdir()


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
    assert not user_status.add_status(status[0], f'new_{status[1]}', status[2])
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


# Tests for picture.py
def test_add_picture(pic):
    '''
    Test each aspect of add_picture
    '''
    # Refuse pictures for non existant users
    assert not picture.add_picture(f'new_{pic[0]}', pic[1])
    # Refuse tags contianing numbers and symbols
    assert not picture.add_picture(pic[0], '#a_num_32')
    assert not picture.add_picture(pic[0], '#a_sym_&stuf')
    # Refuse tag strings longer than 100 characters
    assert not picture.add_picture(pic[0], '#a '*35)
    # Sucessfully add two pictures
    assert picture.add_picture(*pic)
    assert picture.add_picture(*pic)


def test_list_user_images(pic):
    '''
    Test each aspect of list_user_images
    '''
    # Return None when no images
    assert picture.list_user_images(pic[0]) is None
    picture.add_picture(*pic)
    result = picture.list_user_images(pic[0])
    tag_path = pic[0] / picture.tags_to_path(pic[1])
    compare = (pic[0], str(tag_path), picture.id_to_filename(1))
    assert result == [compare]


def test_reconcile_images(pic):
    '''
    Test reconcile_images by adding three pictures
    Remove one from the database, and another from the image directory
    Make sure reconcile_images returns the correct missing images
    '''
    # Add three pictures
    picture.add_picture(*pic)
    picture.add_picture(*pic)
    picture.add_picture(*pic)
    tag_path = pic[0] / picture.tags_to_path(pic[1])
    # Remove the second picture from the image directory
    (tag_path / picture.id_to_filename(2)).unlink()
    with sql.connection(sql.PICTURE) as table:
        table.delete(picture_id=3)
    result = picture.reconcile_images(pic[0])
    file_not_db = {(pic[0], str(tag_path), picture.id_to_filename(3))}
    db_not_file = {(pic[0], str(tag_path), picture.id_to_filename(2))}
    assert result['files-db'] == file_not_db
    assert result['db-files'] == db_not_file


# Tests for main.py
def test_load_users(monkeypatch):
    '''
    Test each aspect of load_users
    '''
    def bad_file(self):  # pylint: disable=W0613
        '''
        Simulates an empty file for testing
        '''
        return iter([])  # Empty file

    header = 'header to be eaten'
    bad_data = [('way', 'too', 'many', 'params', 'test'),  # Too many parameters
                ('not', 'enough', 'params'),  # Not enough parameters
                ('', 'missing1@info.bk', 'one', 'name'),  # Empty user_id
                ('missing2', '', 'two', 'name'),  # Empty email
                ('missing3', 'missing3@info.bk', '', 'name'),  # Empty name
                ('missing4', 'missing4@info.bk', 'four', '')]  # Empty last name
    assert main.load_users('accounts.csv')  # Test sucessful inserts
    assert not main.load_users('accounts')  # Refuse non csv files
    monkeypatch.setattr(csv, 'reader', bad_file)
    assert not main.load_users('accounts.csv')  # Refuse empty files
    for test in bad_data:
        user_data = [header] + [test]
        csv.reader = Mock(return_value=iter(user_data))
        assert not main.load_users('accounts.csv')  # Refuse to use bad data


def test_load_status_updates(monkeypatch):
    '''
    Test each aspect of load_status_updates
    '''
    def bad_file(self):  # pylint: disable=W0613
        '''
        Simulates an empty file for testing
        '''
        return iter([])  # Empty file

    header = 'header to be eaten'
    bad_data = [('too', 'many', 'params', 'test'),  # Too many parameters
                ('not_enough', 'params'),  # Not enough parameters
                ('', 'one', 'message'),  # Empty status_id
                ('missing2', '', 'message'),  # Empty user_id
                ('missing3', 'three', '')]  # Empty message
    assert main.load_status_updates('status_updates.csv')  # Test sucessful inserts
    assert not main.load_status_updates('status_updates')  # Refuse non csv files
    monkeypatch.setattr(csv, 'reader', bad_file)
    assert not main.load_status_updates('status_updates.csv')  # Refuse empty files
    for test in bad_data:
        status_data = [header] + [test]
        csv.reader = Mock(return_value=iter(status_data))
        assert not main.load_status_updates('status_updates.csv')  # Refuse to use bad data


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


def test_picture_interfaces(pic):
    '''
    Test functions that interface with picture
    '''
    assert main.upload_picture(*pic)
