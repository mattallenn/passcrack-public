import hashlib, os
import sqlite3
from cryptography.fernet import Fernet
import string
import random
from colorama import Fore, Back, Style
import getpass
import subprocess
from tabulate import tabulate
import csv

# Syncs Database
def sync():
    try:
        commit_message = "updated database"
        subprocess.run(["git", "pull"])
        subprocess.run(["git", "add", "passwords.db"])
        subprocess.run(["git", "commit", "-m", commit_message])
        subprocess.run(["git", "push"])
    except:
        print("Unable to push to github")

# Export Database to csv
def export():
    cur.execute("SELECT * FROM passwords")
    data = cur.fetchall()

    with open("output.csv", "w", newline="\n") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

# Displays all passwords
def display_all():
    #Fetches data
    cur.execute("SELECT * FROM passwords")
    data = cur.fetchall()
    
    decrypted_data = []

    for row in data:
        username = row[0]
        url = row[1]
        password = row[2]

        decrypted_password = f.decrypt(password).decode("utf-8")
        decrypted_row = (username, url, decrypted_password) 
        
        decrypted_data.append(decrypted_row)

    # Print the table
    print(tabulate(decrypted_data, headers=["Username", "URL", "Password"], tablefmt='grid'))

#checks if password matches
def login_success():
    
    # NEED TO ADD FUNCTIONALITY FOR USER TO CREATE NEW PASSWORD. 
    # FOR NOW, HASH YOUR PASSWORD USING A SHA256 HASH GENERATOR AND REPLACE THE HASHED PASSWORD BELOW
    # THIS WILL BE CHANGED SOON
    if hashed_password == "":
        print("Welcome, you have successfully logged in!")
        line()
        return True

#Hashes password
def hash_password(password):
    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()

    # Convert the password to bytes and update the hash object
    sha256.update(password.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_password = sha256.hexdigest()

    return hashed_password

#lookup password
def lookup_password(url):
    data = fetch_password(url)
    print("Username: ", data[0])
    print("URL: ", data[1])
    print("Password: ", (f.decrypt(data[2]).decode("utf-8")))

#Add password function
def add_password(username, url, password):
    cur.execute("INSERT INTO passwords VALUES (?, ?, ?)", 
                (username, url, password))
    con.commit()

#Lookup password
def fetch_password(url):
    #Retrieves Data
    data = cur.execute("SELECT * FROM passwords WHERE url = ?", [url])
    data = cur.fetchone()

    return(data)

#Generate secure password
def generate_password():

    password_list = [] 
    for i in range(24):
        current_char = random.choice(string.hexdigits + string.punctuation) 
        password_list.append(current_char)
    new_password = ''.join(password_list)
    
    return new_password


#Prints line the width of terminal
def line():
    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    line = '-' * terminal_width
    print(line)

#Connects DB
#Allows user to input database file path
try:
    db_path = open("db_path.txt", "r")
    with open("db_path.txt", "r") as file:
        db = file.read()

    con = sqlite3.connect(db)

except:
    print("Database file path is not yet specified.") 
    db_path = input("Enter file path: ")
    new_file = open("db_path.txt", "w")
    new_file.write(db_path)
    con = sqlite3.connect(db_path)
#Creates cursor to iterate over DB

cur = con.cursor()

#Generates Encryption Key
key = bytes(b'Hxlwpcb0o2vUXbPfJlS8pesYYj6g8DJMZvL6UnLrejE=')
f = Fernet(key)

print(Fore.GREEN+ r""" ____                ____                _    
|  _ \ __ _ ___ ___ / ___|_ __ __ _  ___| | __
| |_) / _` / __/ __| |   | '__/ _` |/ __| |/ /
|  __/ (_| \__ \__ \ |___| | | (_| | (__|   < 
|_|   \__,_|___/___/\____|_|  \__,_|\___|_|\_\

""")

password_input = getpass.getpass()
hashed_password = hash_password(password_input)

if login_success() != True:
    print("Get the fuck outta here man!")
    exit()

#Loops program
cont = 0
while cont == 0: 

    #Prompts user to generate password or 
    try:
        choice = int(input("Enter 0 to continue\nEnter 1 to add password\nEnter 2 to lookup password\nEnter 3 to generate secure password\nEnter 4 to display all passwords\nEnter 5 to sync database\nEnter 6 to export csv file"))
     #Add password 
        if choice == 1:
            username = input("Enter username: ")
            url = input("Enter url: ")
            password = f.encrypt(bytes(input("Enter password: "), encoding='utf8'))
            add_password(username, url, password)
        #Lookup password
        elif choice == 2:
            url = input("Enter url: ")
            lookup_password(url)
        #Generate Secure Password
        elif choice == 3:
            print(generate_password())
        #Displays all
        elif choice == 4:
            display_all()
        # Syncs database to github
        elif choice == 5:
            commit_message = "updated database"
            subprocess.run(["git", "pull"])
            subprocess.run(["git", "add", "passwords.db"])
            subprocess.run(["git", "commit", "-m", commit_message])
            subprocess.run(["git", "push"])
        elif choice == 6:
            line()
            sync()
        
        elif choice == 0:
            line()
            continue
    except:
        line()
        exit()
    
    
    line()

# Close database
con.close()
