'''
Tests the timing and memory use of assignment 3
'''
import cProfile
import pstats
from timeit import timeit as timer
from memory_profiler import profile
import main


@profile
def baseline():
    '''
    Method needed for memory profiling
    '''
    user_baseline = main.init_user_collection()
    status_baseline = main.init_status_collection()
    main.load_users('accounts.csv', user_baseline)
    main.load_status_updates('status_updates.csv', status_baseline)
    main.add_user('dave03', 'dave@three.org', 'Dave', 'Jones', user_baseline)
    main.add_status('dave03', 'dave03_01', 'Random text', status_baseline)
    main.update_user('dave03', 'dave@new.gov', 'Dave', 'Rex', user_baseline)
    main.update_status('dave03', 'dave03_01', 'Whos in charge now', status_baseline)
    main.search_user('dave03', user_baseline)
    main.search_status('dave03_01', status_baseline)
    main.delete_status('dave03_01', status_baseline)
    main.delete_user('dave03', user_baseline)


print('Timeit Data')
# Setup benchmarks
users = main.init_user_collection()
statuses = main.init_status_collection()
# Profiling with timeit
print('Load Users')
print(timer("main.load_users('accounts.csv', users)",
             globals=globals(),
             number=1
))
print('Load Status Updates')
print(timer("main.load_status_updates('status_updates.csv', statuses)",
             globals=globals(),
             number=1
))
print('Add User')
print(timer("main.add_user('dave03', 'dave@three.org', 'Dave', 'Jones', users)",
             globals=globals(),
             number=1
))
print('Add Status')
print(timer("main.add_status('dave03', 'dave03_01', 'Random text', statuses)",
             globals=globals(),
             number=1
))
print('Update User')
print(timer("main.update_user('dave03', 'dave@new.gov', 'Dave', 'Rex', users)",
             globals=globals(),
             number=1
))
print('Update Status')
print(timer("main.update_status('dave03', 'dave03_01', 'Whos in charge now', statuses)",
             globals=globals(),
             number=1
))
print('Search User')
print(timer("main.search_user('dave03', users)",
             globals=globals(),
             number=1
))
print('Search Status')
print(timer("main.search_status('dave03_01', statuses)",
             globals=globals(),
             number=1
))
print('Delete Status')
print(timer("main.delete_status('dave03_01', statuses)",
             globals=globals(),
             number=1
))
print('Delete User')
print(timer("main.delete_user('dave03', users)",
             globals=globals(),
             number=1
))

print('cProfile Data')
statuses.table.drop_table()
users.table.drop_table()
users = main.init_user_collection()
statuses = main.init_status_collection()
# Profiling with cProfile
pr = cProfile.Profile()
pr.enable()
main.load_users('accounts.csv', users)
pr.disable()
ps = pstats.Stats(pr).strip_dirs().sort_stats('tottime')
ps.print_stats(15)

print('Memory Profiler Data')
statuses.table.drop_table()
users.table.drop_table()
# Profiling with Memory Profiler
baseline()
