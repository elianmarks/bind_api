# -*- coding: utf-8 -*-
#Elliann Marks
#elian.markes@gmail.com
#

import sqlite3
from cli.config import USERS_DB
import hashlib

conn = None
cursor = None

def pwdhash(inp):
    return hashlib.md5(inp).hexdigest()

def connect():
    global conn, cursor
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()

def install():
    create_table = """CREATE TABLE IF NOT EXISTS  bindrestusers(
    username VARCHAR(200) PRIMARY KEY,
    password VARCHAR(200),
    restgroup VARCHAR(30) DEFAULT 'restuser',
    enabled INT DEFAULT 1,
    updated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table)
    return True

def reinstall():
    drop_table = "DROP TABLE IF EXISTS bindrestusers"
    cursor.execute(drop_table)

    create_table = """CREATE TABLE bindrestusers(
    username VARCHAR(200) PRIMARY KEY,
    password VARCHAR(200),
    restgroup VARCHAR(30) DEFAULT 'restuser',
    enabled INT DEFAULT 1,
    updated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_table)
    return True

def useradd(username, password, group):
    query = """INSERT OR IGNORE INTO bindrestusers(
    username, password, restgroup
    ) VALUES(?, ?, ?)
    """
    cursor.execute(query, (username, pwdhash(password), group))
    if cursor.rowcount > 0:
        conn.commit()
        return True
    else:
        return False

def usermod(username, group):
    query = """UPDATE bindrestusers SET
    restgroup = ? WHERE username = ?
    """
    cursor.execute(query, (group, username))
    if cursor.rowcount > 0:
        conn.commit()
        return True
    else:
        return False

def userdel(username):
    query = """DELETE FROM bindrestusers
    WHERE username = ?
    """
    cursor.execute(query, (username, ))
    if cursor.rowcount > 0:
        conn.commit()
        return True
    else:
        return False

def passwd(username, password):
    query = """UPDATE bindrestusers SET
    password = ? WHERE username = ?
    """
    cursor.execute(query, (pwdhash(password), username))
    if cursor.rowcount > 0:
        conn.commit()
        return True
    else:
        return False

def authenticate(username, password, groups):
    query = """
    SELECT username, restgroup FROM bindrestusers WHERE
    username = ? AND password = ?
    """
    cursor.execute(query, (username, pwdhash(password)))
    row = cursor.fetchone()
    if row is None:
        return False

    if row[1] in groups:
        return True

    return False

def exists(username):
    query = """
    SELECT username FROM bindrestusers WHERE username = ?
    """
    cursor.execute(query, (username, ))
    rows = cursor.fetchall()
    return True if rows else False

def get():
    users = []
    query = """
    SELECT username, restgroup FROM bindrestusers WHERE enabled = 1
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        users.append((row[0], row[1]))
    return users
