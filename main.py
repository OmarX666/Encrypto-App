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

        # Connect to the SQLite database
        conn = sqlite3.connect(current_script_dir + r"\Assets\users.db")
        cursor = conn.cursor()

        # Create the users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL)
        ''')

        conn.commit()
        conn.close()

        # logging setup
        logging.basicConfig(
            filename=f"{current_script_dir}\Assets\logs.log",
            filemode='a',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        logging.info("Files have been created.")

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

    # Connect to the SQLite database
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(current_script_dir + r"\Assets\users.db")
    cursor = conn.cursor()
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
            "INSERT INTO users VALUES (?, ?, ?, ?)", (random_id,useNam, useEm, usePass)
            )
        conn.commit()
        conn.close()

        # Add To UserInfo to config.json
        with open(current_script_dir + r"\Assets\config.json", 'w') as config_file:
            config_file.write(json.dumps(
                {
                    "user_id": random_id,
                    "username": useNam,
                    "email": useEm,
                    "password": usePass,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                indent=2
            ))

        print("User created successfully!")
        logging.info(f"User {useNam} created successfully.")
        return True

def main():
    """
    Main function to handle the core logic of the application.
    """

    if not files_prep():
        print("Hello, welcome to Encrypto!")

        while True:
            # Validate username format using regex
            if len(username := input("Enter your username: ").strip()) >= 3 and len(username) <= 20:
                break
            else:
                print("Invalid username format. Please use 3-20 alphanumeric characters or underscores.")

        while True:
            # Validate password length
            if len(password := input("Enter your password: ").strip()) >= 8:
                break
            else:
                print("Password must be at least 8 characters long. Please try again.")

        while True:
            Email = input("Enter your email: ").strip()
            # Validate email format using regex
            if re.match(r"[^@]+@[^@]+\.[^@]+", Email):
                break
            else:
                print("Invalid email format. Please try again.")

        while True:
            if Sign_up(username, Email, password):
                break
    else:  
        pass


if __name__ == "__main__":
    main()