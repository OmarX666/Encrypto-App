from datetime import datetime
import sqlite3, re, os, json
import logging, random

# Check if All files exist, if not create them

def files_prep():
    """
    Function to check if all necessary files exist.
    If a file does not exist, it will be created.
    """
    # Get the current script directory
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(f"{current_script_dir}\Assets"):
        os.makedirs(f"{current_script_dir}\Assets", exist_ok=True)

    # List of files to check
    files = [   
        current_script_dir + r"\Assets\users.db", 
        current_script_dir + r"\Assets\config.json",
        current_script_dir + r"\Assets\logs.log"
        ]
    exist = [os.path.exists(file) for file in files]
    if all(exist):
        return True  # All files exist, no need to create them
    else:
        for file in files:
            with open(file, 'a') as f:
                f.close()  # Create an empty file

        return False


def check_user_in():
    pass

def Sign_in(username, password):
    """
    Function to handle user sign-in.
    This function checks if the user exists in the database and validates the password.
    """

def Sign_up(useNam, useEm, usePass):
    """
    Function to handle user sign-in.
    This function checks if the user exists in the database and validates the password.
    """

    print("User registered successfully!")

def main():
    """
    Main function to handle the core logic of the application.
    """

    if not files_prep():
        print("Hello, welcome to Encrypto!")

        usernamme = input("Enter your username: ").strip()
        Email = input("Enter your email: ").strip()
        password = input("Enter your password: ").strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", Email):
            print("Invalid email format. Please try again.")
            return

        Sign_up(usernamme, Email, password)
    else:  
        pass


if __name__ == "__main__":
    main()