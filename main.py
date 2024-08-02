import sqlite3
import getpass
import bcrypt
from controller import *

# Connect to the database
master_conn = sqlite3.connect('users.db')

# Create a table to store usernames and passwords
master_conn.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL);''')

def retrieve_data(username):
    # Connect to the user's database
    user_conn = sqlite3.connect(f'{username}.db')

    # Retrieve all data from the "data" table
    query = "SELECT * FROM data"
    result = user_conn.execute(query).fetchall()

    # Print the retrieved data
    print(f'Data for user {username}:')
    for row in result:
        print(row)
        
    
    # Close the connection to the user's database
    user_conn.close()

def create_user(master_conn):
    # Keep prompting the user for a unique username
    while True:
        username = input('Enter a username: ')

        # Check if the username already exists in the master database
        query = "SELECT * FROM users WHERE username = ?"
        params = (username,)
        result = master_conn.execute(query, params)

        if result.fetchone():
            print('Username already exists. Please enter a unique username.')
            continue

        # Prompt the user to enter a password
        password = getpass.getpass(prompt='Enter a password: ')

        # Generate a random salt and hash the password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

        # Insert the username, password hash, and salt into the master database
        query = "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)"
        params = (username, password_hash, salt)
        master_conn.execute(query, params)
        master_conn.commit()
        print('User created successfully.')
            
        return username
    
def login_user(username, password):
    # Prompt the user to enter their username and password
    #username = input('Username: ')
    #password = getpass.getpass(prompt='Password: ')

    # Connect to the master database and retrieve the user's password hash and salt
    query = "SELECT password_hash, salt FROM users WHERE username = ?"
    params = (username,)
    result = master_conn.execute(query, params).fetchone()

    if result is None:
        # If the username doesn't exist, return None
        print('Invalid username or password.')
        return None

    stored_password_hash, salt = result

    # Hash the entered password with the stored salt and compare it to the stored password hash
    entered_password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password_hash):
        print('Invalid username or password.')
        return None

    # Connect to the user's database
    user_conn = sqlite3.connect(f'{username}.db')

    # Create a table in the user's database if it doesn't already exist
    user_conn.execute('''CREATE TABLE IF NOT EXISTS data
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value TEXT NOT NULL);''')

    #Extracting the data from the user's database
    retrieve_data(username)
    
    # Return the connection to the user's database
    return user_conn

def login():
    print("Create new user [1]" )
    print("Login to database [2]")
    choice = input("Enter yout choice [1/2]: ")
    
    if choice == '1':
        create_user(master_conn)
    elif choice == '2':
        username = input("Username: ")
        password = input("Password: ")
        
        login_user(username, password)



def main():   
    login()
    
if __name__ == '__main__':
    main()