### Sequential processing
As something to compare to, this is the timing for Load Users and Load Status Updates before adding multiprocessing

```Timeit Data
Load Users
0.07722080000000009
Load Status Updates
2.4718242
```

### Multiprocessing
Using cpu_count() returned 12 cores for my system, so I initially sized the chunks to created ten processes each, resulting in slower times than sequential processing

```
chunksize = 200, 20000
Timeit Data
Load Users
1.7228275999999996
Load Status Updates
3.3752047000000003
```

For the sake of completion, I used trial and error to attempt to narrow down the optimal chunk size.
Oddly this resulted in 2 processes for Load Users, and 12 processes for Load Status Updates.
Load Users was still 10 times slower and Load Status Updates 30% slower with multiprocessing

```
chunksize = 1000, 16670
Timeit Data
Load Users
1.0311677000000001
Load Status Updates
3.242783900000001

```

I do not know of any optimization techniques to make my multiprocessing implementation more efficient, so currently this implementation adds too much overhead to be worth using

