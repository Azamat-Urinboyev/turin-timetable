import mysql.connector
from datetime import datetime
import pandas as pd

class Database:
    def __init__(self, user, password) -> None:
        database_name = "timetable"
        users_table = """CREATE TABLE IF NOT EXISTS users(
        id BIGINT NOT NULL,
        name VARCHAR(50),
        username VARCHAR(255),
        university VARCHAR(30),
        group_name VARCHAR(20),
        PRIMARY KEY (id)
        )"""

        self.connection = mysql.connector.connect(
            host="localhost",
            user=user,
            password=password
        )
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")

        self.connection.connect(database=database_name)
        self.cursor.execute(users_table)
        self.connection.commit()
        self.connection.close()
        print("Database is set up.")

    def insert_user(self, user_id, full_name, username):
        self.connection.connect()
        sql_query = "INSERT INTO users (id, name, username) VALUES (%s, %s, %s)"
        self.cursor.execute(sql_query, (user_id, full_name, username))
        self.connection.commit()
        self.connection.close()


    def user_exist(self, user_id):
        self.connection.connect()
        sql_query = "SELECT * FROM users WHERE id=%s"
        self.cursor.execute(sql_query, (user_id,))
        data = self.cursor.fetchone()
        self.connection.close()
        if data == None:
            return False
        return True
    
    def insert_univer(self, user_id, university):
        self.connection.connect()
        sql_query = "UPDATE users SET university=%s WHERE id=%s"
        self.cursor.execute(sql_query, (university, user_id))
        self.connection.commit()
        self.connection.close()

    def insert_group(self, user_id, group):
        self.connection.connect()
        sql_query = "UPDATE users SET group_name=%s WHERE id=%s"
        self.cursor.execute(sql_query, (group, user_id))
        self.connection.commit()
        self.connection.close()

    def get_univer_group(self, user_id):
        self.connection.connect()
        sql_query = "SELECT university, group_name FROM users WHERE id=%s"
        self.cursor.execute(sql_query, (user_id,))
        data = self.cursor.fetchone()
        self.connection.close()
        return data
    
    def get_all_data(self):
        self.connection.connect()
        sql_query = "SELECT * FROM users"
        self.cursor.execute(sql_query)
        data = self.cursor.fetchall()
        self.connection.close()
        return data
    
    def get_all_users(self):
        self.connection.connect()
        sql_query = "SELECT id FROM users"
        self.cursor.execute(sql_query)
        data = self.cursor.fetchall()
        self.connection.close()
        return data
    
    def remove_user(self, user_id):
        self.connection.connect()
        sql_query = "DELETE FROM users WHERE id=%s"
        self.cursor.execute(sql_query, (user_id,))
        self.connection.commit()
        self.connection.close()