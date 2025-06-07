from datetime import datetime
import sqlite3, re, os, json
import logging

# Check if All files exist, if not create them

def check_files():
    """
    Function to check if all necessary files exist.
    If a file does not exist, it will be created.
    """
    files = ['users.db', 'config.json', 'logs.log']
    for file in files:
        if not os.path.exists(file):
            with open(file, 'a') as f:
                pass  # Create an empty fil
            f.close()
            return False
        else:
            return True


def check_user_in():
    pass

def Sign_in(username, password):
    """
    Function to handle user sign-in.
    This function checks if the user exists in the database and validates the password.
    """

def main():
    """
    Main function to handle the core logic of the application.
    """

    check_files()


if __name__ == "__main__":
    main()