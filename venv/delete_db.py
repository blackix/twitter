import os

if os.path.exists('tweets.db'):
    os.remove('tweets.db')
    print("Database deleted successfully.")
else:
    print("The database does not exist.")
