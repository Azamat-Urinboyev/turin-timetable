import sqlite3

class Database:
    def __init__(self) -> None:
        users_table = """CREATE TABLE IF NOT EXISTS users(
        id BIGINT NOT NULL,
        name VARCHAR(50),
        username VARCHAR(255),
        university VARCHAR(30),
        group_name VARCHAR(20),
        PRIMARY KEY (id)
        )"""

        self.connection = sqlite3.connect("./data/users.db", check_same_thread=False)
        self.cursor = self.connection.cursor()

        self.cursor.execute(users_table)
        self.connection.commit()
        print("Database is set up.")

    def insert_user(self, user_id, full_name, username):
        sql_query = "INSERT INTO users (id, name, username) VALUES (?,  ?,  ?)"
        self.cursor.execute(sql_query, (user_id, full_name, username))
        self.connection.commit()
         


    def user_exist(self, user_id):
        sql_query = "SELECT * FROM users WHERE id=?"
        self.cursor.execute(sql_query, (user_id,))
        data = self.cursor.fetchone()
        if data == None:
            return False
        return True
    
    def insert_univer(self, user_id, university):
        sql_query = "UPDATE users SET university= ? WHERE id=?"
        self.cursor.execute(sql_query, (university, user_id))
        self.connection.commit()
        

    def insert_group(self, user_id, group):
        sql_query = "UPDATE users SET group_name= ? WHERE id=?"
        self.cursor.execute(sql_query, (group, user_id))
        self.connection.commit()
        

    def get_univer_group(self, user_id):
        sql_query = "SELECT university, group_name FROM users WHERE id=?"
        self.cursor.execute(sql_query, (user_id,))
        data = self.cursor.fetchone()
        return data
    
    def get_all_data(self):
        sql_query = "SELECT * FROM users"
        self.cursor.execute(sql_query)
        data = self.cursor.fetchall()
        return data
    
    def get_all_users(self):
        sql_query = "SELECT id FROM users"
        self.cursor.execute(sql_query)
        data = self.cursor.fetchall() 
        return data
    
    def remove_user(self, user_id):
        sql_query = "DELETE FROM users WHERE id=?"
        self.cursor.execute(sql_query, (user_id,))
        self.connection.commit()
         