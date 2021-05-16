'''
Unit Tests for main, users, and user_status
'''
# pylint: disable=R0902
# pylint: disable=R0904
from unittest import TestCase
from unittest.mock import Mock, call, patch
import csv
import os
import main
import users
import user_status


class MainTest(TestCase):
    '''
    Unit Tests for main
    '''
    def setUp(self):
        '''
        Provide fixture for testing main
        '''
        self.accounts = main.init_user_collection()
        self.statuses = main.init_status_collection()
        self.user_csv = 'accounts.csv'
        self.status_csv = 'status_updates.csv'
        self.filename = 'testfile.csv'
        self.user_id = 12
        self.status_id = 10
        self.user = (self.user_id, 'email@name.com', 'Pauline', 'Martinez')
        self.status = (self.status_id, self.user_id, "Somthing here")
        self.user_data = (('header to be eaten'),
                          ('evmiles97', 'eve.miles@uw.edu', 'Eve', 'Miles'),
                          ('dave03', 'david.yuen@gmail.com', 'David', 'Yuen'))
        self.status_data = (('header to be eaten'),
                            ('evmiles97_00001', 'evmiles97', 'Compiling'),
                            ('dave03_00001', 'dave03', 'Sunny in Seattle'),
                            ('evmiles97_00002', 'evmiles97', 'Hike'))
        self.bad_user_data = (['name'],
                              ('way', 'too', 'many', 'params', 'test'),
                              ('', 'missing@info.bk', 'one', 'name'),
                              ('missing2', '', 'two', 'name'),
                              ('missing3', 'missing@info.bk', '', 'name'),
                              ('missing4', 'missing@info.bk', 'four', ''))
        self.bad_status_data = (['name'],
                                ('way', 'too', 'many', 'params', 'test'),
                                ('', 'one', 'message'),
                                ('missing2', '', 'message'),
                                ('missing3', 'three', ''))

    def tearDown(self):
        try:
            os.remove(self.filename)
        except FileNotFoundError:
            pass

    def test_init_user_collection(self):
        '''
        Test that a UserCollection is created
        '''
        self.assertIsInstance(self.accounts, users.UserCollection)

    def test_init_status_collection(self):
        '''
        Test that a UserStatusCollection is created
        '''
        self.assertIsInstance(self.statuses, user_status.UserStatusCollection)

    def test_load_users(self):
        '''
        Test that user data is retrived correctly
        '''
        csv.reader = Mock(return_value=iter(self.user_data))
        self.accounts.add_user = Mock(return_value=True)
        calls = [call(*data) for data in self.user_data[1:]]
        self.assertTrue(main.load_users(self.user_csv, self.accounts))
        self.accounts.add_user.has_calls(calls)
        # Assert that repeated entries do not throw errors
        csv.reader.return_value = iter(self.user_data)
        self.accounts.add_user = Mock(return_value=False)
        self.assertTrue(main.load_users(self.user_csv, self.accounts))
        self.accounts.add_user.assert_has_calls(calls)

    def test_load_users_error(self):
        '''
        Test that bad data throws errors correctly
        '''
        # Ensure each fault is tested seperatly
        header = ['header to be eaten']
        self.accounts.add_user = Mock()
        for test in self.bad_user_data:
            test = [header] + [test]
            csv.reader = Mock(return_value=iter(test))
            self.assertFalse(main.load_users(self.user_csv, self.accounts))
        self.assertFalse(main.load_users(self.user_csv[:-4], self.accounts))
        self.accounts.add_user.assert_not_called()

    @patch('csv.writer')
    def test_save_users(self, mocked_writer):
        '''
        Test that user data is saved correctly
        '''
        # Set Up for this test
        mocked_writer.return_value = Mock()
        header = ['USER_ID', 'EMAIL', 'NAME', 'LASTNAME']
        calls = [call(header)]
        for data in self.user_data[1:]:
            self.accounts.add_user(*data)
            calls.append(call([*data]))
        # Run and test save_users
        self.assertTrue(main.save_users(self.filename, self.accounts))
        self.assertTrue(os.path.isfile(self.filename))
        mocked_writer.return_value.writerow.assert_has_calls(calls)

    @patch('csv.writer')
    def test_save_users_error(self, mocked_writer):
        '''
        Test that an invalid filename throws an error
        '''
        mocked_writer.return_value = Mock()
        self.assertFalse(main.save_users(self.filename[:-4], self.accounts))
        self.assertFalse(os.path.isfile(self.filename[:-4]))
        mocked_writer.return_value.writerow.assert_not_called()

    def test_load_status_updates(self):
        '''
        Test that status data is retrived correctly
        '''
        csv.reader = Mock(return_value=iter(self.status_data))
        self.statuses.add_status = Mock(return_value=True)
        calls = [call(*data) for data in self.status_data[1:]]
        self.assertTrue(main.load_status_updates(self.status_csv,
                                                 self.statuses))
        self.statuses.add_status.has_calls(calls)
        # Assert that repeated entries do not throw errors
        csv.reader.return_value = iter(self.status_data)
        self.statuses.add_status = Mock(return_value=False)
        self.assertTrue(main.load_status_updates(self.status_csv,
                                                 self.statuses))
        self.statuses.add_status.assert_has_calls(calls)

    def test_load_status_updates_error(self):
        '''
        Test that bad data throws errors correctly
        '''
        # Ensure each fault is tested seperatly
        header = ['header to be eaten']
        self.statuses.add_status = Mock()
        for test in self.bad_status_data:
            test = [header] + [test]
            csv.reader = Mock(return_value=iter(test))
            self.assertFalse(main.load_status_updates(self.status_csv,
                                                      self.statuses))
        self.assertFalse(main.load_status_updates(self.status_csv[:-4],
                                                  self.statuses))
        self.statuses.add_status.assert_not_called()

    @patch('csv.writer')
    def test_save_status_updates(self, mocked_writer):
        '''
        Test that statuses are saved correctly
        '''
        mocked_writer.return_value = Mock()
        header = ['STATUS_ID', 'USER_ID', 'STATUS_TEXT']
        calls = [call(header)]
        for data in self.status_data[1:]:
            self.statuses.add_status(*data)
            calls.append(call([*data]))
        self.assertTrue(main.save_status_updates(self.filename, self.statuses))
        self.assertTrue(os.path.isfile(self.filename))
        mocked_writer.return_value.writerow.assert_has_calls(calls)

    @patch('csv.writer')
    def test_save_status_updates_error(self, mocked_writer):
        '''
        Test that an invalid filename throws an error
        '''
        mocked_writer.return_value = Mock()
        self.assertFalse(main.save_status_updates(self.filename[:-4],
                                                  self.statuses))
        self.assertFalse(os.path.isfile(self.filename[:-4]))
        mocked_writer.return_value.writerow.assert_not_called()

    def test_add_user(self):
        '''
        Test that users.add_user is called correctly
        '''
        self.accounts.add_user = Mock(return_value=True)
        main.add_user(*self.user, self.accounts)
        self.accounts.add_user.assert_called_with(*self.user)

    def test_update_user(self):
        '''
        Test that users.modify_user is called correctly
        '''
        self.accounts.modify_user = Mock(return_value=True)
        main.update_user(*self.user, self.accounts)
        self.accounts.modify_user.assert_called_with(*self.user)

    def test_delete_user(self):
        '''
        Test that users.delete_user is called correctly
        '''
        self.accounts.delete_user = Mock(return_value=True)
        main.delete_user(self.user_id, self.accounts)
        self.accounts.delete_user.assert_called_with(self.user_id)

    def test_search_user(self):
        '''
        Test that users.search_user is called correctly
        '''
        test_user = users.Users(1, 'a@b.com', 'AB', 'CD')
        self.accounts.search_user = Mock(return_value=test_user)
        result = main.search_user(self.user_id, self.accounts)
        self.accounts.search_user.assert_called_with(self.user_id)
        self.assertEqual(type(result), users.Users)

    def test_search_user_dne(self):
        '''
        Test that search_user returns None
        when users.search_user return an empty user
        '''
        none_user = users.Users(None, None, None, None)
        self.accounts.search_user = Mock(return_value=none_user)
        result = main.search_user(self.user_id, self.accounts)
        self.assertIsNone(result)

    def test_add_status(self):
        '''
        Test that user_status.add_status is called correctly
        '''
        self.statuses.add_status = Mock(return_value=True)
        main.add_status(self.user_id, self.status_id, self.status[2],
                        self.statuses)
        self.statuses.add_status.assert_called_with(*self.status)

    def test_update_status(self):
        '''
        Test that user_status.modify_status is called correctly
        '''
        self.statuses.modify_status = Mock(return_value=True)
        main.update_status(*self.status, self.statuses)
        self.statuses.modify_status.assert_called_with(*self.status)

    def test_delete_status(self):
        '''
        Test that user_status.delete_user is called correctly
        '''
        self.statuses.delete_status = Mock(return_value=True)
        main.delete_status(self.status_id, self.statuses)
        self.statuses.delete_status.assert_called_with(self.status_id)

    def test_search_status(self):
        '''
        Test that user_status.search_status is called correctly
        '''
        test_status = user_status.UserStatus(1, 2, 'sample')
        self.statuses.search_status = Mock(return_value=test_status)
        result = main.search_status(self.status_id, self.statuses)
        self.statuses.search_status.assert_called_with(self.status_id)
        self.assertEqual(type(result), user_status.UserStatus)

    def test_search_status_dne(self):
        '''
        Test that search_status returns None
        when user_status.search_status returns an empty status
        '''
        none_status = user_status.UserStatus(None, None, None)
        self.statuses.search_status = Mock(return_value=none_status)
        result = main.search_status(self.status_id, self.statuses)
        self.assertIsNone(result)


class UsersTest(TestCase):
    '''
    Unit Tests for users
    '''
    def setUp(self):
        '''
        Provide fixture for testing users
        '''
        self.user_one = (42, 'name@site.com', 'Frank', 'Smith')
        self.user_two = (18, 'singer@khe.com', 'Judy', 'Sofer')
        self.items = users.UserCollection()
        self.items.add_user(*self.user_one)

    def test_users_init(self):
        '''
        Test that an Users is created correctly
        '''
        user = users.Users(*self.user_one)
        self.assertEqual(user.user_id, self.user_one[0])
        self.assertEqual(user.email, self.user_one[1])
        self.assertEqual(user.user_name, self.user_one[2])
        self.assertEqual(user.user_last_name, self.user_one[3])

    def test_user_collection_init(self):
        '''
        Test that an UserCollection is created correctly
        '''
        # This test requires an empty UserCollection
        items = users.UserCollection()
        self.assertEqual(items.database, dict())

    def test_add_user(self):
        '''
        Test that a user has been added to the collection
        '''
        # Uses user added during setup
        self.assertIn(self.user_one[0], self.items.database)

    def test_add_user_already_exists(self):
        '''
        Test that adding a duplicate user throws an error
        '''
        self.assertFalse(self.items.add_user(*self.user_one))
        self.assertIn(self.user_one[0], self.items.database)

    def test_modify_user(self):
        '''
        Test that users are modified correctly
        '''
        new_last_name = 'Jones'
        self.assertTrue(self.items.modify_user(*self.user_one[0:3],
                        new_last_name))
        database = self.items.database  # to satisfy flake8
        modified_last_name = database[self.user_one[0]].user_last_name
        self.assertEqual(modified_last_name, new_last_name)

    def test_modify_user_dne(self):
        '''
        Test that modifying a nonexistant user throws an error
        '''
        self.assertFalse(self.items.modify_user(*self.user_two))

    def test_delete_user(self):
        '''
        Test that users are deleted correctly
        '''
        self.assertTrue(self.items.delete_user(self.user_one[0]))
        self.assertNotIn(self.user_one[0], self.items.database)

    def test_delete_user_dne(self):
        '''
        Test that deleting a nonexistant user throws an error
        '''
        self.assertFalse(self.items.delete_user(self.user_two[0]))
        self.assertNotIn(self.user_two[0], self.items.database)

    def test_search_user(self):
        '''
        Test that users can be found correctly
        '''
        self.items.add_user(*self.user_two)
        found = self.items.search_user(self.user_one[0])
        self.assertEqual(found.user_name, self.user_one[2])
        found = self.items.search_user(self.user_two[0])
        self.assertEqual(found.email, self.user_two[1])

    def test_search_user_dne(self):
        '''
        Test that nonexistant users are not found
        '''
        found = self.items.search_user(self.user_two[0])
        self.assertIsNone(found.user_id)


class UserStatusTest(TestCase):
    '''
    Unit Tests for UserStatusTest
    '''
    def setUp(self):
        '''
        Provide fixture for testing user_status
        '''
        self.status_one = (1, 42, "Bland")
        self.status_two = (2, 42, "Statement")
        self.items = user_status.UserStatusCollection()
        self.items.add_status(*self.status_one)

    def test_user_status_init(self):
        '''
        Test that an UserStatus is created correctly
        '''
        status = user_status.UserStatus(*self.status_one)
        self.assertEqual(status.status_id, self.status_one[0])
        self.assertEqual(status.user_id, self.status_one[1])
        self.assertEqual(status.status_text, self.status_one[2])

    def test_user_status_collection_init(self):
        '''
        Test that an UserStatusCollection is created correctly
        '''
        items = user_status.UserStatusCollection()
        self.assertEqual(items.database, dict())

    def test_add_status(self):
        '''
        Test that statuses are added correctly
        '''
        self.assertIn(self.status_one[0], self.items.database)

    def test_add_status_already_exists(self):
        '''
        Test that duplicate statuses throw an error
        '''
        self.assertFalse(self.items.add_status(*self.status_one))
        self.assertIn(self.status_one[0], self.items.database)

    def test_modify_status(self):
        '''
        Test that statuses are modified correctly
        '''
        new_text = "Happy"
        self.assertTrue(self.items.modify_status(*self.status_one[0:2],
                                                 new_text))
        modified_text = self.items.database[self.status_one[0]].status_text
        self.assertEqual(modified_text, new_text)

    def test_modify_status_dne(self):
        '''
        Test that modifiying a nonexistant status throws an error
        '''
        self.assertFalse(self.items.modify_status(*self.status_two))

    def test_delete_status(self):
        '''
        Test that statuses are deleted correctly
        '''
        self.assertTrue(self.items.delete_status(self.status_one[0]))
        self.assertNotIn(self.status_one[0], self.items.database)

    def test_delete_status_dne(self):
        '''
        Test that deleting a nonexistant status throws an error
        '''
        self.assertFalse(self.items.delete_status(self.status_two[0]))
        self.assertNotIn(self.status_two[0], self.items.database)

    def test_search_status(self):
        '''
        Test that statuses are found correctly
        '''
        self.items.add_status(*self.status_two)
        found = self.items.search_status(self.status_one[0])
        self.assertEqual(found.status_text, self.status_one[2])
        found = self.items.search_status(self.status_two[0])
        self.assertEqual(found.user_id, self.status_two[1])

    def test_search_status_dne(self):
        '''
        Test that nonexistant statuses are not found
        '''
        found = self.items.search_status(self.status_two[0])
        self.assertIsNone(found.user_id)
