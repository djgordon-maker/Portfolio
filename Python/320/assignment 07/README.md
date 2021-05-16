# Introduction

On this assignment, we will try to speed up the loading process of CSV files into your MongoDB database by applying multiprocessing. 

# What you need to do

Take a look at the code below:

```Python
import pandas as pd

def import_csv_in_chunks(size=10):
    '''
    Imports CSV file in chunks of a defined size
    '''
    chunk_number = 0
    for chunk in pd.read_csv('accounts.csv', chunksize=size, iterator=True):
        print(f"CHUNK {chunk_number}")
        for index, row in chunk.iterrows():
            print(f"{row['USER_ID']} {row['EMAIL']} {row['NAME']} {row['LASTNAME']}")
        chunk_number += 1

if __name__ == "__main__":
    import_csv_in_chunks()
```

You can learn about the Pandas module [here](https://pandas.pydata.org/).

The piece of code above shows you how to use Pandas to import a CSV file in chunks of a defined size. 

You will need to apply this to your functions to load users and load status updates in *main.py*. 

You will also need to create a couple of worker functions that will take one chunk of data from CSV files and add the corresponding entries to the right collection in the database. You can either have a configurable worker function that can add data to both the users and user status collections or two functions, one for each.

Each worker function will run inside of a separate process that will be launched from the corresponding loader function.

# Your submission

* Include the following files:
    * *menu.py*.
    * *main.py*.
    * *user_status.py*.
    * *users.py*.
* Write a short report on your results, including performance improvements and how different chunk sizes affected that performance.
* Do not include CSV files.

# Tips

* Collect timing data before converting your loading code to multiprocessing, that will be your baseline.
* For this to work, you will need each worker function to establish its own separate connection to the database. The connection cannot be shared (feel free to give that a try).
* Load the users first, as your database should have restrictions in place to prevent status updates added for users that do not exist.
* The sample data being provided has 2,000 user accounts, so the difference in loading times might not be as dramatic. However, for status updates the count is 200,000 so any improvements should be noticeable.
* DO NOT join your processes immediately after launching them! That would force them to run sequentially, blocking any performance improvement. Instead, after you start each process, append the new process to a list. Once all your processes have started (i.e., no chunks of data left), do another *for* loop to iterate over the list of process, joining each process.
* Calling *multiprocessing.cpu_count()* will give you the number **logical cores** your system has. This will usually be double the amount of physical cores (i.e., if you are on a quad-core system, it will return 8), because each core usually has two threads, each of which makes up a logical core. The number of logical cores and the total number of records to insert could be an important consideration in finding the optimal chunk size.