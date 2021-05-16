Ran pylint first, found that main.update_user() wasn't called with enough parameters
Also noticed that load_users() tried to use user_selection inplace of user_collection

### Testing User
* Moved upper() to store the uppercase version of user input
* search_user() called name inplace of user_name
* corrected search_user() to check if result exists during error checking 

### Testing Status
* Found that update_status() uses main.add_status(); should use main.update_status()
* had to rearrange parameters to match the new call
* search_status also needs to check if result exists during error checking