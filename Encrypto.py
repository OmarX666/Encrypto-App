import os, logging, sqlite3
import json, random, re
import time, sys
from datetime import datetime
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
from typing import Tuple, List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        conn = sqlite3.connect(self.db_path)
        return conn, conn.cursor()

    def initialize(self) -> None:
        conn, cursor = self.get_connection()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL)
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Folders (
                UserID INTEGER,
                FolderName TEXT NOT NULL,
                FolderPath TEXT NOT NULL)
        ''')
        conn.commit()
        conn.close()

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_file:
                return json.load(config_file)
        return {}

    def save(self, data: Dict[str, Any]) -> None:
        with open(self.config_path, 'w') as config_file:
            json.dump(data, config_file, indent=2)

class UserManager:
    def __init__(self, db_manager: DatabaseManager, config_manager: ConfigManager):
        self.db_manager = db_manager
        self.config_manager = config_manager

    def id_gen(self) -> int:
        conn, cursor = self.db_manager.get_connection()
        while True:
            id = random.randint(1, 1000000)
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
            if cursor.fetchone() is None:
                break
        conn.close()
        return id

    def sign_up(self, username: str, email: str, password: str) -> bool:
        conn, cursor = self.db_manager.get_connection()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? and email = ? and password = ?", (username, email, password)
        )
        if cursor.fetchone() is not None:
            print("User already exists. Please try a different username or email.")
            logging.warning(f"User {username} already exists.")
            choice = input("Do you want to sign in instead? (yes/no): ").strip().lower()
            if choice == 'yes':
                print("Redirecting to sign-in...")
                logging.info(f"User {username} chose to sign in instead.")
                conn.close()
                self.sign_in(username, password)
                return True
            else:
                print("Please try again with a different username or email.")
                logging.info(f"User {username} chose to sign up again.")
                conn.close()
                return False
        else:
            user_id = self.id_gen()
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, username, email, password)
            )
            conn.commit()
            conn.close()
            self.config_manager.save({
                "user_id": user_id,
                "username": username,
                "email": email,
                "password": password,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "folders": []
            })
            print("User created successfully!")
            logging.info(f"User {username} created successfully.")
            return True

    def sign_in(self, username: str, password: str) -> bool:
        conn, cursor = self.db_manager.get_connection()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? and password = ?", (username, password)
        )
        user_values = cursor.fetchone()
        if user_values is not None:
            cursor.execute(
                "SELECT * FROM Folders WHERE UserID = ?", (user_values[0],)
            )
            folders = cursor.fetchall()
            folders_list = [{
                "name": folder[1],
                "path": folder[2]
            } for folder in folders]
            self.config_manager.save({
                "user_id": user_values[0],
                "username": username,
                "email": user_values[2],
                "password": password,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "folders": folders_list
            })
            logging.info(f"User {username} signed in successfully.")
            conn.close()
            return True
        else:
            print("Invalid username or password. Please try again.")
            return False

class FolderManager:
    def __init__(self, db_manager: DatabaseManager, config_manager: ConfigManager):
        self.db_manager = db_manager
        self.config_manager = config_manager

    def select_folder(self) -> Optional[str]:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = askdirectory(title="Select a folder", initialdir=os.getcwd(), mustexist=True)
        root.destroy()
        if folder_path:
            return self.save_folder(folder_path, os.path.basename(folder_path), self.config_manager.load()["user_id"])
        else:
            print("Please select a folder to continue.")
            return None

    def save_folder(self, folder_path: str, folder_name: str, user_id: int) -> Optional[str]:
        try:
            conn, cursor = self.db_manager.get_connection()
            config_data = self.config_manager.load()
            cursor.execute("SELECT * FROM Folders WHERE FolderPath = ? and UserID = ?", (folder_path, user_id))
            if cursor.fetchone() is not None:
                logging.warning(f"Folder {folder_path} already exists in the database.")
                print(f"Folder {folder_path} already exists. Please select a different folder.")
                return self.select_folder()
            else:
                cursor.execute("INSERT INTO Folders VALUES (?, ?, ?)", 
                            (user_id, folder_name, folder_path))
                logging.info(f"Folder {folder_path} selected and saved to database.")
                conn.commit()
                conn.close()
            if "folders" not in config_data:
                config_data["folders"] = []
            config_data["folders"].append({
                "name": folder_name,
                "path": folder_path
            })
            self.config_manager.save(config_data)
        except Exception:
            logging.error("Error saving folder to database or config.json.")
            print("An error occurred while saving the folder. Please try again.")
            return self.select_folder()
        except sqlite3.Error as e:
            logging.error(f"SQLite error: {e}")
            print("An error occurred while accessing the database. Please try again.")
            quit(0)
        return None

    def select_file(self, path: str) -> Optional[str]:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = askopenfilename(title="Select a file", initialdir=path)
        root.destroy()
        return file_path

    def spinning_loader(self, count: int) -> None:
        print("Loading Files...", end="")
        spinner = ['-', '\\', '|', '/']
        for _ in range(count):
            for char in spinner:
                sys.stdout.write('\rLoading Files... ' + char)
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write('\rLoading... Done!   \n')
        sys.stdout.flush()

class EncryptoApp:
    def __init__(self):
        self.db_manager = DatabaseManager(USERS_DB)
        self.config_manager = ConfigManager(CONFIG_JSON)
        self.user_manager = UserManager(self.db_manager, self.config_manager)
        self.folder_manager = FolderManager(self.db_manager, self.config_manager)
        self.initialize_assets()

    def initialize_assets(self) -> None:
        if not os.path.exists(ASSETS_DIR):
            os.makedirs(ASSETS_DIR, exist_ok=True)
            return False

        files = [USERS_DB, CONFIG_JSON, LOGS_LOG]
        if all([os.path.exists(file) for file in files]):
            return True
        else:
            for file in files:
                with open(file, 'a') as f:
                    f.close()

            self.db_manager.initialize()
            logging.basicConfig(
                filename=LOGS_LOG,
                filemode='a',
                level=logging.INFO,
                datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)s - %(levelname)s- %(message)s'
            )
            logging.info("Files have been created.")
            return False

    def get_user_input(self, username: bool = False, email: bool = False, password: bool = False) -> List[str]:
        while True:
            if not username: 
                break
            if len(username := input("Enter your username: ").strip()) >= 3 and len(username) <= 20:
                break
            else:
                print("Invalid username format. Please use 3-20 alphanumeric characters or underscores.")

        while True:
            if not email:
                break
            email = input("Enter your email: ").strip()
            if re.match(r"^[A-z0-9\.]{3,}@[A-z0-9]+\.(com|net|org|info)$", email):
                break
            else:
                print("Invalid email format. Please try again.")

        while True:
            if not password:
                break
            if len(password := input("Enter your password: ").strip()) >= 8:
                break
            else:
                print("Password must be at least 8 characters long. Please try again.")

        return [username, email, password]

    def user_not_found(self) -> None:
        while True:
            choice = input("Do you want to sign up or sign in? (sign up/sign in): ").strip().lower()
            if choice == 'sign up':
                while True:
                    username, email, password = self.get_user_input(True, True, True)
                    if self.user_manager.sign_up(username, email, password):
                        break
                break
            elif choice == 'sign in':
                while True:
                    username, _, password = self.get_user_input(True, False, True)
                    if self.user_manager.sign_in(username, password):
                        break
                break
            else:
                print("Invalid choice. Please try again.")

    def run(self) -> None:
        if not self.initialize_assets():
            print("welcome to Encrypto!")
            while True:
                username, Email, password = self.get_user_input(True, True, True)
                if self.user_manager.sign_up(username, Email, password):
                    break

            config_data = self.config_manager.load()
            print("Please, select a folder.")
            folder = self.folder_manager.select_folder()
            print(f"Selected folder: {folder}")
        else:  
            try:
                config_data = self.config_manager.load()
                conn, cursor = self.db_manager.get_connection()
                cursor.execute(
                    "SELECT * FROM users WHERE id = ? and username = ? and email = ? and password = ?", 
                        (config_data["user_id"], config_data["username"], config_data["email"], config_data["password"]))
                if cursor.fetchone() is not None:
                    print(f"Welcome, {config_data['username']}!")
                    logging.info(f"User {config_data['username']} signed in successfully.")
                    choice = input("Do you want to select a folder or use an existing one or exit? (select/use/exit): ").strip().lower()
                    if choice == 'select':
                        folder = self.folder_manager.select_folder()
                        quit(1)
                    elif choice == 'use':

                        # Selecting a folder
                        print("Please, select a folder.")
                        while True:
                            if "folders" in config_data:
                                for folder in enumerate(config_data["folders"], start=1):
                                    print(f"folder {folder[0]}: {folder[1]['name']}")
                                folder_choice = input("Enter the name of the folder you want to use: ").strip().lower()
                                folder_path = next((f["path"] for f in config_data["folders"] if f["name"].lower() == folder_choice), None)
                                if folder_path is not None:
                                    break
                                else:
                                    print("Please select a valid folder.")
                            else:
                                self.folder_manager.select_folder()

                        # Selecting a file
                        print(f"Using folder: {folder_path}")
                        Files_list = os.listdir(folder_path)
                        self.folder_manager.spinning_loader(len(Files_list))
                        for file in enumerate(Files_list, start=1):
                            print(f"File {file[0]} {file[1]}")

                        while True:
                            file_choice = int(input("Enter the number of the folder you want to use: ").strip())
                            try:
                                print(Files_list[file_choice - 1])
                                break
                            except:
                                print("Please select a valid file number.")

                        # Sending the file

                    elif choice == 'exit':
                        print("Exiting the application.")
                        quit(0)
                else:
                    print("User not found. Please sign up or Sign in.")
                    self.user_not_found()
                    self.run()
                conn.close()
            except json.JSONDecodeError as e:
                print("Error reading config file.")
                logging.error(f"JSON decode error: {e}")
                self.user_not_found()
                self.run()

if __name__ == "__main__":

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
    USERS_DB = os.path.join(ASSETS_DIR, "users.db")
    CONFIG_JSON = os.path.join(ASSETS_DIR, "config.json")
    LOGS_LOG = os.path.join(ASSETS_DIR, "logs.log")

    app = EncryptoApp()
    app.run()