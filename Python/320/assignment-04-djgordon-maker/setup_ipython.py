'''
Import into ipython for easier testing
'''
import peewee as pw  # pylint: disable = W0611
import main


user = main.init_user_collection()
status = main.init_status_collection()
main.load_users('accounts.csv', user)
main.load_status_updates('status_updates.csv', status)
