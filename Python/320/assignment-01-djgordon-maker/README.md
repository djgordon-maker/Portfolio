# Introduction 

You have been tasked with developing a basic backend for a company's internal social network. Initially, this social network with only allow users to post status updates ("Feeling happy today", "Excited to be learning Advanced Python", etc.). 

Some early work had already been made. Unfortunately, that code was lost, leaving only two files containing comma-separated values. These files are named *accounts.csv* and *status_updates.csv*.

*accounts.csv*, as its name indicates, contains user account information. The first line is a header, indicating what information is under each column. For example:

```
USER_ID, EMAIL, NAME, LASTNAME
evmiles97, eve.miles@uw.edu, Eve, Miles
dave03, david.yuen@gmail.com, David, Yuen
```

*status_updates.csv*, on the other hand, looks like this:

```
STATUS_ID, USER_ID, STATUS_TEXT
evmiles97_00001, evmiles97, "Code is finally compiling"
dave03_00001, dave03, "Sunny in Seattle this morning"
evmiles97_00002, evmiles97, "Perfect weather for a hike"
```

# Your base files (TDD)

The assignment folder already contains three files:

* *users.py*
* *user_status.py*
* *main.py*

The first two are already fully coded and you will not need (or are allowed to) modify them. *main.py*, on the other hand, contains only stubs that you will need to code.
	
# How does it work

*main.py* will import *user_status.py* and *users.py* and be able to complete the following tasks:
 
1. Create a new instance of *UserCollection*.
1. Load user data from a CSV file into an instance of *UserCollection*.
1. Create a new instance of *UserStatusCollection*.
1. Load status data from a CSV file into an instance of *UserStatusCollection*.
1. Perform different operations (add, update, delete, search) on the *User* and *UserStatus* collections.


# Test-Driven Development (TDD)

## Testing

Before writing any code into *main.py*, create a file called *test_main.py*, which will contain your unit tests. Your unit tests will follow these requirements:

* You need to individually test all functions and methods within *main.py*, *users.py* and *user_status.py*.
* Try to use *Mock()* and *Patch()* at least **once** to isolate your tests. For example, if you are testing *delete_user()* in *main.py*, your code will probably need to call *delete_user()* in *users*.py. Use *Mock()* or *Patch()* to override the response from *users.UserCollection.delete_user()*.
* Note that you might need multiple tests of multiple assertions on the same function or method in order to cover several scenarios.

Coverage analysis must show **100% test coverage on all files** once your code is ready to be tested.

**As you write your code inside of *main.py*, make sure you add one or more tests in *test_main.py* to target the code that you just added. In this way, your tests will be ready at the same time as the rest of your code.**

## Additional considerations for testing

 Make sure you add tests for error conditions as well, including those triggering exceptions. Think what happens if:

* Parameters are missing.
* Parameters are invalid (for example, a user_id value that contains spaces).
* There are empty fields.

# Other requirements

* You can add additional methods and functions to *main.py* as required. Note that coverage requirements will still be enforced.
* Do not add additional fields to users or status updates. Those will come later in the course.
* Remember to do coverage analysis and include additional tests if your coverage is lower than the requirement.
* Run a Pylint or a similar tool to ensure your code is PEP8 compliant. Your code should be graded at 10 out of 10 when tested with Pylint. It is possible to use a custom .pylintrc file of Pylint disable statements to selectively disable some rules that do not make sense with your code. If you do that, please note that the instructor might still ask you to correct the issues related to the disabled rules.
* If you use exception handling (try/except), do not use bare exceptions. For example, if you add exception handling for the case in which an input file cannot be found, make that exception explicitly for FileNotFoundError. Bare exceptions are ok when you are experimenting, but not a good idea for code that will be released.

# Submission

Your submission should include the following files:

* main.py.
* users.py.
* user_status.py
* test_main.py.
* accounts.csv (if required by your testing).
* status_updates.csv (if required by your testing).
* .pylintrc (if using custom rules).

# How will your code be evaluated?

The instructor will do the following:

1. Run your tests and confirm that no tests are failing.
1. Run coverage analysis and verify that test coverage meets the requirements.
1. Run *Pylint* using your custom *.pylintrc* and/or Pylint disable statements and confirm that code is rated at 10 out of 10.
1. Run *Pylint* with all rules enabled and confirm no major PEP8 compliance issues are detected.

# Additional tips #

* Use the *csv* library, included in Python for all your file operations with csv files.
* In Python 3, you iterate through the values in a dictionary by iterating going over *dict.values()*, where *dict* is the name of your dictionary.
* If you use a *setUp()* method in your tests, keep in mind that it will run **before** every test, effectively resetting some of your variables.
* The same goes for the *tearDown()* method, which will run after each one of your tests. Using both *setUp()* and *tearDown()* is optional.
* Remember that *unittest* executes tests in **alphabetical** order, so *test_a* will run before *test_b*. This is one of the reasons you should not have dependencies between unit tests.
* When testing *search_user()* and *search_status()*, keep in mind that those functions will return instances of *Users* and *UserStatus*, so you might need to consider asserting for fields such as *last_name* within those instances.