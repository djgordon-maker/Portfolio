# Assignment 6

I started profiling by timing each function under each implimentation earning me the following results

### Sqlite
```
Load Users
0.06827700000000003
Load Status Updates
8.7930917
Add User
0.027180599999999444
Add Status
0.0338585000000009
Update User
0.033372599999999863
Update Status
0.0007376000000007821
Search User
0.0003913000000004274
Search Status
0.0005702999999996905
Delete Status
0.03140440000000133
Delete User
0.033530700000000024
```

### MongoDB
```
Load Users
0.0746696
Load Status Updates
2.6223739
Add User
0.002465900000000243
Add Status
0.004834799999999806
Update User
0.003992800000000241
Update Status
0.0953242000000003
Search User
0.003045999999999882
Search Status
0.09840530000000003
Delete Status
0.09614769999999995
Delete User
0.10176379999999963

```

I found that Sqlite is faster than MongoDB for most functions, except for adding entries to the database.
I noticed that Load Users broke this pattern so I did a deeper dive into that method using cProfile, results below

### Sqlite
```
         240676 function calls (228336 primitive calls) in 0.136 seconds

   Ordered by: internal time
   List reduced from 180 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.060    0.060    0.060    0.060 {method 'commit' of 'sqlite3.Connection' objects}
     8000    0.010    0.000    0.023    0.000 peewee.py:618(value)
       21    0.007    0.000    0.007    0.000 {method 'execute' of 'sqlite3.Cursor' objects}
       20    0.006    0.000    0.062    0.003 peewee.py:2577(_generate_insert)
  2040/40    0.006    0.000    0.049    0.001 peewee.py:1756(__sql__)
 10360/20    0.004    0.000    0.063    0.003 peewee.py:606(sql)
    20260    0.004    0.000    0.005    0.000 peewee.py:614(literal)
    44669    0.003    0.000    0.004    0.000 {built-in method builtins.isinstance}
        1    0.003    0.003    0.136    0.136 main.py:41(load_users)
     2080    0.003    0.000    0.005    0.000 peewee.py:522(__call__)
    42441    0.003    0.000    0.003    0.000 {method 'append' of 'list' objects}
     8000    0.002    0.000    0.025    0.000 peewee.py:1369(__sql__)
     8000    0.002    0.000    0.002    0.000 peewee.py:1357(__init__)
     8100    0.002    0.000    0.003    0.000 peewee.py:536(__getattr__)
     2080    0.002    0.000    0.007    0.000 peewee.py:576(__call__)
```

### MongoDB
```
         61981 function calls (61943 primitive calls) in 0.371 seconds

   Ordered by: internal time
   List reduced from 535 to 15 due to restriction <15>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
       20    0.325    0.016    0.325    0.016 {method 'acquire' of '_thread.lock' objects}
        4    0.019    0.005    0.019    0.005 {method 'recv_into' of '_socket.socket' objects}
        1    0.005    0.005    0.006    0.006 {built-in method pymongo._cmessage._batched_op_msg}
        1    0.004    0.004    0.371    0.371 main.py:41(load_users)
     2001    0.003    0.000    0.004    0.000 objectid.py:175(__generate)
     2001    0.002    0.000    0.012    0.000 collection.py:748(gen)
     6010    0.001    0.000    0.003    0.000 {built-in method _abc._abc_instancecheck}
     4067    0.001    0.000    0.004    0.000 {built-in method builtins.isinstance}
     2002    0.001    0.000    0.001    0.000 {built-in method _abc._abc_subclasscheck}
     6010    0.001    0.000    0.004    0.000 abc.py:137(__instancecheck__)
     2001    0.001    0.000    0.001    0.000 objectid.py:165(_random)
     2000    0.001    0.000    0.004    0.000 common.py:499(validate_is_document_type)
     4002    0.001    0.000    0.001    0.000 {built-in method _struct.pack}
     8070    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
     2000    0.000    0.000    0.001    0.000 bulk.py:82(add)
```

As you can see cProfile spent more time runing {method 'acquire' of '_thread.lock' objects} than timeit spent runing load_users in its entireity, so this does not apear to be a useful comparison
I also used memory profiler to see which implimentation takes more memory.  Neither takes very much, but mongoDB is less efficient

### Sqlite
```
Filename: benchmark.py

Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    11     47.3 MiB     47.3 MiB           1   @profile
    12                                         def baseline():
    13                                             ```
    14                                             Method needed for memory profiling
    15                                             ```
    16     47.3 MiB      0.0 MiB           1       user_baseline = main.init_user_collection()
    17     47.3 MiB      0.0 MiB           1       status_baseline = main.init_status_collection()
    18     47.8 MiB      0.5 MiB           1       main.load_users('accounts.csv', user_baseline)
    19     49.3 MiB      1.4 MiB           1       main.load_status_updates('status_updates.csv', status_baseline)
    20     49.3 MiB      0.0 MiB           1       main.add_user('dave03', 'dave@three.org', 'Dave', 'Jones', user_baseline)
    21     49.3 MiB      0.0 MiB           1       main.add_status('dave03', 'dave03_01', 'Random text', status_baseline)
    22     49.3 MiB      0.0 MiB           1       main.update_user('dave03', 'dave@new.gov', 'Dave', 'Rex', user_baseline)
    23     49.3 MiB      0.0 MiB           1       main.update_status('dave03', 'dave03_01', 'Whos in charge now', status_baseline)
    24     49.3 MiB      0.0 MiB           1       main.search_user('dave03', user_baseline)
    25     49.3 MiB      0.0 MiB           1       main.search_status('dave03_01', status_baseline)
    26     49.3 MiB      0.0 MiB           1       main.delete_status('dave03_01', status_baseline)
    27     49.3 MiB      0.0 MiB           1       main.delete_user('dave03', user_baseline)
```

### MongoDB
```
Filename: benchmark.py

Line #    Mem usage    Increment  Occurences   Line Contents
============================================================
    11     55.3 MiB     55.3 MiB           1   @profile
    12                                         def baseline():
    13                                             ```
    14                                             Method needed for memory profiling
    15                                             ```
    16     55.4 MiB      0.2 MiB           1       user_baseline = main.init_user_collection()
    17     55.6 MiB      0.2 MiB           1       status_baseline = main.init_status_collection()
    18     55.6 MiB      0.0 MiB           1       main.load_users('accounts.csv', user_baseline)
    19     61.4 MiB      5.8 MiB           1       main.load_status_updates('status_updates.csv', status_baseline)
    20     61.0 MiB     -0.4 MiB           1       main.add_user('dave03', 'dave@three.org', 'Dave', 'Jones', user_baseline)
    21     61.1 MiB      0.1 MiB           1       main.add_status('dave03', 'dave03_01', 'Random text', status_baseline)
    22     61.2 MiB      0.1 MiB           1       main.update_user('dave03', 'dave@new.gov', 'Dave', 'Rex', user_baseline)
    23     61.3 MiB      0.1 MiB           1       main.update_status('dave03', 'dave03_01', 'Whos in charge now', status_baseline)
    24     61.3 MiB      0.0 MiB           1       main.search_user('dave03', user_baseline)
    25     61.3 MiB      0.0 MiB           1       main.search_status('dave03_01', status_baseline)
    26     61.3 MiB      0.0 MiB           1       main.delete_status('dave03_01', status_baseline)
    27     61.3 MiB     -0.0 MiB           1       main.delete_user('dave03', user_baseline)
```

Overall, the difference in performance is minor, but I give Sqlite the edge because I expect that we will be doing more searching than anything and Sqlite completes a search roughly ten times faster than MongoDB
However the larger impact is from implimentation.  Given the simple and strict relationship between users and statuses I recomend Sqlite.  I would only go with MongoDB if we wanted the freedom to change our minds later.
Also I'm more familiar with SQL than NoSQL and had an eaiser time getting Sqlite working compared with MongoDB