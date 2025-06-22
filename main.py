import os
import logging
import sqlite3
import json
import random
import re
# Encrypto - A simple file for encryption tools
import crypt
from datetime import datetime
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
USERS_DB = os.path.join(ASSETS_DIR, "users.db")
CONFIG_JSON = os.path.join(ASSETS_DIR, "config.json")
LOGS_LOG = os.path.join(ASSETS_DIR, "logs.log")

def get_db_connection():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    return conn, cursor

def load_config():
    with open(CONFIG_JSON, 'r') as config_file:
        return json.load(config_file)

def save_config(data):
    with open(CONFIG_JSON, 'w') as config_file:
        json.dump(data, config_file, indent=2)

# Check if All files exist, if not create them
def initialize_assets():
    """
    Function to check if all necessary files exist.
    If a file does not exist, it will be created.
    """
    # Get the current script directory
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)

    # List of files to check 
    files = [USERS_DB, CONFIG_JSON, LOGS_LOG]

    if all([os.path.exists(file) for file in files]):
        return True  # All files exist, no need to create them
    else:
        for file in files:
            with open(file, 'a') as f:
                f.close()  # Create an empty file

        # Connect to the SQLite database
        conn, cursor = get_db_connection()

        # Create the users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL)
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Folders (
                id INTEGER,
                FolderName TEXT NOT NULL,
                FolderPath TEXT NOT NULL)
        ''')

        conn.commit()
        conn.close()

        # logging setup
        logging.basicConfig(
            filename=LOGS_LOG,
            filemode='a',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s - %(levelname)s- %(message)s'
        )

        logging.info("Files have been created.")
        return False

def Getting_user_input(username = False, Email = False, password = False):
    """
    Function to get user input for username, email, and password.
    This function is currently a placeholder and does not implement any functionality.
    """
    
    while True:
        if not username: 
            break

        # Validate username format using regex
        if len(username := input("Enter your username: ").strip()) >= 3 and len(username) <= 20:
            break
        else:
            print("Invalid username format. Please use 3-20 alphanumeric characters or underscores.")

    while True:
        if not Email:
            break

        Email = input("Enter your email: ").strip()
        # Validate email format using regex
        if re.match(r"[^@]+@[^@]+\.[^@]+", Email):
            break
        else:
            print("Invalid email format. Please try again.")

    while True:
        if not password:
            break

        # Validate password length
        if len(password := input("Enter your password: ").strip()) >= 8:
            break
        else:
            print("Password must be at least 8 characters long. Please try again.")

    return [username, Email, password]

def Sign_in(username, password):
    """
    Function to handle user sign-in.
    This function checks if the user exists in the database.

        Args:
            username (str): The username of the user trying to sign in.
            password (str): The password of the user trying to sign in.

        Returns:
            bool: True if the user was found and signed in successfully, False otherwise.

    """
    conn, cursor = get_db_connection()
    # Check if the user exists in the database
    cursor.execute(
        "SELECT * FROM users WHERE username = ? and password = ?", (username, password)
        )
    
    User_values = cursor.fetchone()

    if User_values is not None:
        cursor.execute(
            "SELECT * FROM Folders WHERE id = ?", (User_values[0],)
        )

        folders = cursor.fetchall()
        folders_list = [{
            "name": folder[1],
            "path": folder[2]
        } for folder in folders]

        # add to config.json
        with open(CONFIG_JSON, 'w') as config_file:
            json.dump({
                "user_id": User_values[0],
                "username": username,
                "email": User_values[2],
                "password": password,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "folders": folders_list
            }, config_file, indent=2)

        logging.info(f"User {username} signed in successfully.")
        conn.close()
        return True
    else:
        print("Invalid username or password. Please try again.")
        return False

def Sign_up(useNam, useEm, usePass):
    """
    Function to handle user sign-in.
    This function checks if the user exists in the database.

    Args:
        useNam (str): The username of the user trying to sign up.
        useEm (str): The email of the user trying to sign up.
        usePass (str): The password of the user trying to sign up.

    Returns:
        bool: True if the user was created successfully, False otherwise.
    """

    # Connect to the SQLite database
    conn, cursor = get_db_connection()
    # Check if the user already exists
    cursor.execute(
        "SELECT * FROM users WHERE username = ? and email = ? and password = ?", (useNam, useEm, usePass)
        )

    if cursor.fetchone() is not None:
        print("User already exists. Please try a different username or email.")
        logging.warning(f"User {useNam} already exists.")
        Choice = input("Do you want to sign in instead? (yes/no): ").strip().lower()
        if Choice == 'yes':
            # Call the sign-in function (not implemented here)
            print("Redirecting to sign-in...")
            logging.info(f"User {useNam} chose to sign in instead.")
            conn.close()
            Sign_in(useNam, usePass)
            return True
        else:
            print("Please try again with a different username or email.")
            logging.info(f"User {useNam} chose to sign up again.")
            conn.close()
            return False
    else:
        # Creating User ID number
        while True:
            random_id = random.random().as_integer_ratio()[random.randint(0, 1)]
            cursor.execute("SELECT * FROM users WHERE id = ?", (random_id,))
            if cursor.fetchone() is None:
                break

        # Insert the new user into the database
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?)", (random_id, useNam, useEm, usePass)
            )
        conn.commit()
        conn.close()

        # Add To UserInfo to config.json
        with open(CONFIG_JSON, 'w') as config_file:
            config_file.write(json.dumps(
                {
                    "user_id": random_id,
                    "username": useNam,
                    "email": useEm,
                    "password": usePass,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "folders": []
                },
                indent=2
            ))

        print("User created successfully!")
        logging.info(f"User {useNam} created successfully.")
        return True

def User_not_found():
    """
    Function to handle the case when a user is not found.
    This function prompts the user to sign up or sign in.
    """
    print("User not found. Please sign up or sign in.")
    while True:
        # Ask the user if they want to sign up or sign in
        choice = input("Do you want to sign up or sign in? (sign up/sign in): ").strip().lower()
        if choice == 'sign up':
            while True:
                username, Email, password = Getting_user_input(True, True, True)
                if Sign_up(username, Email, password):
                    break
            break
        elif choice == 'sign in':
            while True:
                username, _, password = Getting_user_input(True, False, True)
                if Sign_in(username, password):
                    break
            break
        else:
            print("Invalid choice. Please try again.")

def select_folder():
    """
    Opens a GUI interface to allow the user to select a folder.
    Returns the selected folder path as a string.
    """
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Force the dialog to appear on top
    root.attributes('-topmost', True)

    # Open the folder selection dialog
    folder_path = askdirectory(title="Select a folder", initialdir=os.getcwd(), mustexist=True)
    
    # Destroy the root window after selection
    root.destroy()

    if folder_path:
        return folder_path
    else:
        print("Please select a folder to continue.")
        return None

def save_folder(folder_path, folder_name):
    """
    Saves the selected folder path and name to database & the config.json file.

    Args:
        folder_path (str): The path of the selected folder.
        folder_name (str): The name of the selected folder.
    """    

    conn, cursor = get_db_connection()
    config_data = load_config()
    # Check if the folder already exists in the database
    cursor.execute("SELECT * FROM Folders WHERE FolderPath = ?", (folder_path,))
    if cursor.fetchone() is not None:
        logging.warning(f"Folder {folder_path} already exists in the database.")
        print(f"Folder {folder_path} already exists. Please select a different folder.")
        return select_folder()
    else:
        cursor.execute("INSERT INTO Folders VALUES (?, ?, ?)", 
                    (config_data["user_id"], os.path.basename(folder_path), folder_path))

        logging.info(f"Folder {folder_path} selected and saved to database.")
        conn.commit()
        conn.close()

    # Ensure folders key exists
    if "folders" not in config_data:
        config_data["folders"] = []

    # Append new folder information
    config_data["folders"].append({
        "name": folder_name,
        "path": folder_path
    })

    save_config(config_data)


def select_file(path):
    """
    Opens a GUI interface to allow the user to select a file.
    Returns the selected file path as a string.
    """
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Force the dialog to appear on top
    root.attributes('-topmost', True)

    # Open the file selection dialog
    file_path = askopenfilename(title="Select a file", initialdir=path)

    # Destroy the root window after selection
    root.destroy()

    return file_path

def main():
    """
    Main function to handle the core logic of the application.
    """

    if not initialize_assets():
        print("welcome to Encrypto!")
        while True:
            username, Email, password = Getting_user_input(True, True, True)
            if Sign_up(username, Email, password):
                break

        print("Please, select a folder.")
        while True:
            folder = select_folder()
            if folder:
                print(f"Selected folder: {folder}")
                # Save the folder to the database and config.json
                save_folder(folder, os.path.basename(folder))
                break
            else:
                print("No folder selected. Please try again.")

        # for file in enumerate(os.listdir(folder), start=1):
        #     print(f"Processing file {file[0]}: {file[1]}")

        # print("Choose a file to encrypt.")
        # selected_file = select_file(folder)
        # if selected_file:
        #     print(f"Selected file: {selected_file}")
        # else:
        #     print("No file selected.")
        #     quit(1)

    else:  
        try:
            with open(CONFIG_JSON, 'r') as config_file:
                config_data = json.load(config_file)

            conn, cursor = get_db_connection()
            cursor.execute(
                "SELECT * FROM users WHERE id = ? and username = ? and email = ? and password = ?", 
                    (config_data["user_id"], config_data["username"], config_data["email"], config_data["password"]))
            if cursor.fetchone() is not None:
                print(f"Welcome back, {config_data['username']}!")
                logging.info(f"User {config_data['username']} signed in successfully.")

                choice = input("Do you want to select a folder or use an existing one or exit? (select/use/exit): ").strip().lower()
                if choice == 'select':
                    folder = select_folder()
                    if folder:
                        print(f"Selected folder: {folder}")
                        save_folder(folder, os.path.basename(folder))
                    else:
                        print("No folder selected.")
                        quit(1)
                elif choice == 'use':
                    config_data = load_config()
                    while True:
                        if "folders" in config_data:
                            print("Please, select a folder.")
                            for folder in enumerate(config_data["folders"], start=1):
                                print(f"Processing folder {folder[0]}: {folder[1]["name"]}")
                            folder_choice = input("Enter the name of the folder you want to use: ").strip()
                            folder_path = next((f["path"] for f in config_data["folders"] if f["name"] == folder_choice), None)
                        else:
                            select_folder()
                elif choice == 'exit':
                    print("Exiting the application.")
                    quit(0)

            else:
                print("User not found. Please sign up or Sign in.")
                User_not_found()
                main()

        except json.JSONDecodeError as e:
            print("Error reading config file. Please sign up again.")
            logging.error(f"JSON decode error")
            User_not_found()
            main()


if __name__ == "__main__":
    main()