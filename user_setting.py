# Class containing user settings that would be used for profile management tab. 
# Currently only contains a username and a testing interval, but this could be modified to include
# more settings later on.

# Author: Patrick Muller

class UserSetting:
    # Class variable to record all usernames that are currently in use.
    _current_usernames = []

    # constructor
    def __init__(self, username, interval=5):
        # Check if the name is available
        # Throw error if it is not.
        if self.name_available(username):
            UserSetting._current_usernames.append(username)
            self.username = username
            self.interval = interval
        else:
            raise ValueError("username already in use") 

    # updates the username for a specific user.
    # removes their old username from the list of current usernames, and append their new username.
    def update_username(self, new_username):
        # Check if the name is available
        # Throw error if it is not.
        if self.name_available(new_username):
            UserSetting._current_usernames.remove(self.username)
            self.username = new_username
            UserSetting._current_usernames.append(self.username)
        else:
            raise ValueError("username already in use")

    #
    def update_interval(self, new_interval):
        if isinstance(new_interval, int) and new_interval > 0:
            self.interval = new_interval
        else:
            raise TypeError("new_interval must be an int that is greater than 0")

    # Returns True if the username is available, otherwise returns False
    def name_available(self, username):
        return not username in UserSetting._current_usernames
            