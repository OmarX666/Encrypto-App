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
            CREATE TABLE IF NOT EXISTS users (id INTEGER,
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
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + r"\Assets\users.db")
    cursor = conn.cursor()
    # Check if the user exists in the database
    cursor.execute(
        "SELECT * FROM users WHERE username = ? and password = ?", (username, password)
        )
    
    User_values = cursor.fetchone()

    if User_values is not None:

        # add to config.json
        with open(os.path.dirname(os.path.abspath(__file__)) + r"\Assets\config.json", 'w') as config_file:
            json.dump({
                "user_id": User_values[0],
                "username": username,
                "email": User_values[2],
                "password": password,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, config_file, indent=2)

        print(f"Welcome back, {username}!")
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
        username, Email, password = Getting_user_input(True, True, True)
        while True:
            if Sign_up(username, Email, password):
                break
    else:  
        with open(os.path.dirname(os.path.abspath(__file__)) + r"\Assets\config.json", 'r') as config_file:
            config_data = json.load(config_file )

        conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + r"\Assets\users.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE id = ? and username = ? and email = ? and password = ?", 
                (config_data["user_id"], config_data["username"], config_data["email"], config_data["password"]))
        if cursor.fetchone() is not None:
            print(f"Welcome back, {config_data['username']}!")
        else:
            print("User not found. Please sign up or Sign in.")
            while True:
                # Ask the user if they want to sign up or sign in
                choice = input("Do you want to sign up or sign in? (sign up/sign in): ").strip().lower()
                if choice == 'sign up':
                    username, Email, password = Getting_user_input(True, True, True)
                    while True:
                        if Sign_up(username, Email, password):
                            break
                    break
                elif choice == 'sign in':
                    username, _, password = Getting_user_input(True, False, True)
                    while True:
                        if Sign_in(username, password):
                            break
                    break
                else:
                    print("Invalid choice. Please try again.")
            conn.close()
            config_file.close()


if __name__ == "__main__":
    main()