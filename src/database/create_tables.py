"""
John Leeds
create_tables.py
8/6/2002

Script to create tables for Type Racer Logs
"""
import sqlite3

TABLES = {"users": 
        [["username"], ["username", "TEXT"], ["join_date", "INTEGER"],
        ["layout", "TEXT"], ["num_races", "INTEGER"], ["num_chars", "INTEGER"],
        ["num_typo", "INTEGER"], ["type_time", "INTEGER"], ["typo_time",
        "INTEGER"], ["start_time", "INTEGER"], ["last_action", "INTEGER"],
        ["downloaded", "TEXT"]], 
        "words":
        [["user_id", "word"], ["user_id", "INTEGER"], ["word", "TEXT"],
        ["num_typed", "INTEGER"], ["time", "TEXT"],
        ["num_typo", "INTEGER"], ["typo_time", "INTEGER"], ["log", "TEXT"]],
        "char_pairs":
        [["user_id", "char_pair"], ["user_id", "INTEGER"], ["char_pair", "TEXT"],
        ["num_typed", "INTEGER"], ["time", "INTEGER"],
        ["num_typo", "INTEGER"], ["typo_time", "INTEGER"], ["log", "TEXT"]],
        "chars":
        [["user_id", "char"], ["user_id", "INTEGER"], ["char", "TEXT"],
        ["num_typed", "INTEGER"], ["time", "INTEGER"],
        ["num_typo", "INTEGER"], ["typo_time", "INTEGER"], ["log", "TEXT"]],
        }

def generateText(table, values):
    text = f"CREATE TABLE IF NOT EXISTS {table} ("
    prim_keys = values[0]
    for name, data_type in values[1:]:
        text += f"{name} {data_type}, "
    text += f"PRIMARY KEY ({', '.join(prim_keys)}));"
    return text

def makeTables():
    con = sqlite3.connect('../data/database.db')
    cur = con.cursor()
    for table in TABLES:
        cur.execute(generateText(table, TABLES[table]))
        con.commit()
    con.close()

def main():
    makeTables()

if __name__ == "__main__":
    main()
