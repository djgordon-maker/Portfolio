'''
Provides a basic frontend
'''
import sys
import logging
import main
from log import logit


logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


@logit(logger)
def load_users():
    '''
    Loads user accounts from a file
    '''
    filename = input('Enter filename of user file: ')
    main.load_users(filename)


@logit(logger)
def load_status_updates():
    '''
    Loads status updates from a file
    '''
    filename = input('Enter filename for status file: ')
    main.load_status_updates(filename)


@logit(logger)
def add_user():
    '''
    Adds a new user into the database
    '''
    user_id = input('User ID: ')
    email = input('User email: ')
    user_name = input('User name: ')
    user_last_name = input('User last name: ')
    if not main.add_user(user_id, email, user_name, user_last_name):
        print("An error occurred while trying to add new user")
    else:
        print("User was successfully added")


@logit(logger)
def update_user():
    '''
    Updates information for an existing user
    '''
    user_id = input('User ID: ')
    email = input('User email: ')
    user_name = input('User name: ')
    user_last_name = input('User last name: ')
    if not main.update_user(user_id, email, user_name, user_last_name):
        print("An error occurred while trying to update user")
    else:
        print("User was successfully updated")


@logit(logger)
def search_user():
    '''
    Searches a user in the database
    '''
    user_id = input('Enter user ID to search: ')
    result = main.search_user(user_id)
    if not result:
        print("ERROR: User does not exist")
    else:
        print(f"User ID: {result['user_id']}")
        print(f"Email: {result['user_email']}")
        print(f"Name: {result['user_name']}")
        print(f"Last name: {result['user_last_name']}")


@logit(logger)
def delete_user():
    '''
    Deletes user from the database
    '''
    user_id = input('User ID: ')
    if not main.delete_user(user_id):
        print("An error occurred while trying to delete user")
    else:
        print("User was successfully deleted")


@logit(logger)
def add_status():
    '''
    Adds a new status into the database
    '''
    user_id = input('User ID: ')
    status_id = input('Status ID: ')
    status_text = input('Status text: ')
    if not main.add_status(user_id, status_id, status_text):
        print("An error occurred while trying to add new status")
    else:
        print("New status was successfully added")


@logit(logger)
def update_status():
    '''
    Updates information for an existing status
    '''
    user_id = input('User ID: ')
    status_id = input('Status ID: ')
    status_text = input('Status text: ')
    if not main.update_status(status_id, user_id, status_text):
        print("An error occurred while trying to update status")
    else:
        print("Status was successfully updated")


@logit(logger)
def search_status():
    '''
    Searches a status in the database
    '''
    status_id = input('Enter status ID to search: ')
    result = main.search_status(status_id)
    if not result:
        print("ERROR: Status does not exist")
    else:
        print(f"User ID: {result['user_id']}")
        print(f"Status ID: {result['status_id']}")
        print(f"Status text: {result['status_text']}")


@logit(logger)
def delete_status():
    '''
    Deletes status from the database
    '''
    status_id = input('Status ID: ')
    if not main.delete_status(status_id):
        print("An error occurred while trying to delete status")
    else:
        print("Status was successfully deleted")


@logit(logger)
def upload_picture():
    '''
    Uploads a picture to the database
    '''
    user_id = input('Enter User ID of uploader: ')
    tags = input('Enter image tags: ')
    if not main.upload_picture(user_id, tags):
        print("ERROR: User does not exist")
    else:
        print("Image successfully uploaded")


@logit(logger)
def list_pictures():
    '''
    Prints all pictures owned by a user
    '''
    user_id = input('Enter User ID of owner: ')
    pictures = main.list_user_images(user_id)
    print(f'{user_id} owns {len(pictures)} pictures')
    for picture in pictures:
        print(f'{picture[1]}\{picture[2]}')  # pylint: disable=W1401


@logit(logger)
def quit_program():
    '''
    Quits program
    '''
    sys.exit()


if __name__ == '__main__':
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
        'J': delete_status,
        'K': upload_picture,
        'L': list_pictures,
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
                            J: Delete status
                            K: Upload picture
                            L: List pictures
                            Q: Quit

                            Please enter your choice: """)
        user_selection = user_selection.upper()
        if user_selection in menu_options:
            menu_options[user_selection]()
        else:
            print("Invalid option")
