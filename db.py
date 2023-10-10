import sqlite3

class Database:
    
    def __init__(self, name: str):
        self.__connection = sqlite3.connect(name)
        self.__cursor = self.__connection.cursor()
    
    def get_user(self, user_id):
        with self.__connection:
            result = self.__cursor.execute("SELECT * FROM `users` WHERE `id` = ?", (user_id,)).fetchone()
            return result
    
    def get_users(self):
        with self.__connection:
            result = self.__cursor.execute("SELECT * FROM `users`").fetchall()
            return result

    def get_user_by_key(self, key: int):
        with self.__connection:
            result = self.__cursor.execute("SELECT * FROM `users` WHERE `key` = ?", (key, )).fetchone()
            return result

    def key_exist(self, key):
        with self.__connection:
            result = self.__cursor.execute("SELECT `key` FROM `users` WHERE `key` = ?", (key, )).fetchone()
            return result
    
    def set_confirmed(self, confirmed: bool, key: int):
        with self.__connection:
            result = self.__cursor.execute("UPDATE users SET `is_confirmed` = ? WHERE `key` = ?", (confirmed, key,)).fetchone()
            return result
    

    def get_last_id(self, table_name):
        with self.__connection:
            table_name = str("") + table_name
            result = self.__cursor.execute(f"SELECT MAX(id) FROM {table_name}").fetchone()            
            return result[0]


    def set_homework(self, record_id, user_id: int, text: str):
        with self.__connection:
            self.__cursor.execute("INSERT INTO homework (id, user_id, home_text) VALUES(?,?,?)", (record_id, user_id, text,))