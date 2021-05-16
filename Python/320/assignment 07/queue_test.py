'''
Simple test for loading data into database
'''
from multiprocessing import Process, Queue
import main

def fun(queue):
    '''
    Example demenstrating queues
    '''
    queue.put([42, None, 'hello'])

if __name__ == '__main__':
    que = Queue()
    pro = Process(target=fun, args=(que,))
    pro.start()
    print(que.get())    # prints "[42, None, 'hello']"
    pro.join()
    # test main now
    accounts = main.init_user_collection()
    statuses = main.init_status_collection()
    accounts.table.drop()
    statuses.table.drop()
    print(main.load_users('accounts.csv', accounts))
    print(main.load_status_updates('status_updates.csv', statuses))
