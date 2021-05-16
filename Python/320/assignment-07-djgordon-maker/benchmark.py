'''
Tests the timing of load_users and load_status_updates
'''
from timeit import timeit as timer
import main

if __name__ == '__main__':
    # Setup benchmarks
    accounts = main.init_user_collection()
    statuses = main.init_status_collection()
    accounts.table.drop()
    statuses.table.drop()
    # Profiling with timeit
    print('Timeit Data')
    print('Load Users')
    print(timer("main.load_users('accounts.csv', accounts)",
                globals=globals(),
                number=1
    ))
    print('Load Status Updates')
    print(timer("main.load_status_updates('status_updates.csv', statuses)",
                globals=globals(),
                number=1
    ))
