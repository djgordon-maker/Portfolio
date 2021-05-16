'''
Provides a basic frontend
'''
import sys
import main


def load_users():
    '''
    Loads user accounts from a file
    '''
    filename = input('Enter filename of user file: ').strip()
    main.load_users(filename, user_collection)


def load_status_updates():
    '''
    Loads status updates from a file
    '''
    filename = input('Enter filename for status file: ').strip()
    main.load_status_updates(filename, status_collection)


def add_user():
    '''
    Adds a new user into the database
    '''
    user_id = input('User ID: ').strip()
    email = input('User email: ').strip()
    user_name = input('User name: ').strip()
    user_last_name = input('User last name: ').strip()
    if not main.add_user(user_id, email, user_name, user_last_name,
                         user_collection):
        print("An error occurred while trying to add new user")
    else:
        print("User was successfully added")


def update_user():
    '''
    Updates information for an existing user
    '''
    user_id = input('User ID: ').strip()
    email = input('User email: ').strip()
    user_name = input('User name: ').strip()
    user_last_name = input('User last name: ').strip()
    if not main.update_user(user_id, email, user_name, user_last_name,
                            user_collection):
        print("An error occurred while trying to update user")
    else:
        print("User was successfully updated")


def search_user():
    '''
    Searches a user in the database
    '''
    user_id = input('Enter user ID to search: ').strip()
    result = main.search_user(user_id, user_collection)
    if not result:
        print("An error coccured while trying to find user")
    else:
        print(f"User ID: {result['user_id']}")
        print(f"Email: {result['user_email']}")
        print(f"Name: {result['user_name']}")
        print(f"Last name: {result['user_last_name']}")


def delete_user():
    '''
    Deletes user from the database
    '''
    user_id = input('User ID: ').strip()
    if not main.delete_user(user_id, user_collection):
        print("An error occurred while trying to delete user")
    else:
        print("User was successfully deleted")


def add_status():
    '''
    Adds a new status into the database
    '''
    user_id = input('User ID: ').strip()
    status_id = input('Status ID: ').strip()
    status_text = input('Status text: ').strip()
    if not main.add_status(user_id, status_id, status_text, status_collection):
        print("An error occurred while trying to add new status")
    else:
        print("New status was successfully added")


def update_status():
    '''
    Updates information for an existing status
    '''
    user_id = input('User ID: ').strip()
    status_id = input('Status ID: ').strip()
    status_text = input('Status text: ').strip()
    if not main.update_status(status_id, user_id, status_text,
                              status_collection):
        print("An error occurred while trying to update status")
    else:
        print("Status was successfully updated")


def search_status():
    '''
    Searches for a status in the database
    '''
    status_id = input('Enter status ID to search: ').strip()
    result = main.search_status(status_id, status_collection)
    if not result:
        print("An error occurred while tryihg to find status")
    else:
        print(f"User ID: {result['user_id']}")
        print(f"Status ID: {result['status_id']}")
        print(f"Status text: {result['status_text']}")


def search_all_status_updates():
    '''
    Searches for all statuses posted by a specified user
    '''
    user_id = input('Enter user ID: ').strip()
    count, result = main.search_all_status_updates(user_id, status_collection)
    print(f"A total {count} status updates found for {user_id}")
    for status in result:
        answer = input("Would you like to see the next update? (Y/N): ")
        answer = answer.upper().strip()
        if answer == 'Y':
            print(status['status_text'])
        elif answer == 'N':
            break
        else:
            print("Invalid option")
    else:
        print("There are no more updates")


def filter_status_by_string():
    '''
    Search all status updates matching a string
    '''
    target_string = input('Enter the string to search: ').strip()
    result = main.filter_status_by_string(target_string, status_collection)
    for status in result:
        answer = input("Review the next status? (Y/N): ")
        answer = answer.upper().strip()
        if answer == 'Y':
            print(status['status_text'])
            answer = input("Delete this status? (Y/N): ")
            answer = answer.upper().strip()
            if answer == 'Y':
                main.delete_status(status['status_id'], status_collection)
                print('Status deleted')
        else:
            break
    else:
        print("There are no more matches")


def flagged_status_updates():
    '''
    Prints a list of all status updates matching a string
    '''
    target_string = input('Enter the string to search: ').strip()
    result = main.filter_status_by_string(target_string, status_collection)
    statuses = [(item['status_id'], item['status_text']) for item in result]
    for status in statuses:
        print(status)


def delete_status():
    '''
    Deletes status from the database
    '''
    status_id = input('Status ID: ').strip()
    if not main.delete_status(status_id, status_collection):
        print("An error occurred while trying to delete status")
    else:
        print("Status was successfully deleted")


def quit_program():
    '''
    Quits program
    '''
    answer = input("Drop data?")
    if answer.upper() == 'Y':
        user_collection.table.drop()
        status_collection.table.drop()
    sys.exit()


if __name__ == '__main__':
    user_collection = main.init_user_collection()
    status_collection = main.init_status_collection()
    menu_options = {
        'A': load_users,
        'B': load_status_updates,
        'C': add_user,
        'D': update_user,
        'E': search_user,
        'F': delete_user,
        'G': add_status,
        'H': update_status,
        'I': search_status,
        'J': search_all_status_updates,
        'K': filter_status_by_string,
        'L': flagged_status_updates,
        'M': delete_status,
        'Q': quit_program
    }
    while True:
        user_selection = input("""
                            A: Load user database
                            B: Load status database
                            C: Add user
                            D: Update user
                            E: Search user
                            F: Delete user
                            G: Add status
                            H: Update status
                            I: Search status
                            J: Search all statuses by user
                            K: Search all status updates matchin a string
                            L: Show all flagged status updates
                            M: Delete status
                            Q: Quit

                            Please enter your choice: """)
        user_selection = user_selection.upper().strip()
        if user_selection in menu_options:
            menu_options[user_selection]()
        else:
            print("Invalid option")
