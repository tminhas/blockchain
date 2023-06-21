import sqlite3

# Connect to the database
conn = sqlite3.connect('instance\db.sqlite')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# SQL statement to create the table
create_table_query = '''
CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY,
    indx INTEGER,
    bpm INTEGER,
    timestamp DATETIME,
    previous_hash TEXT,
    plc_data TEXT
);
'''

# Execute the create table query
cursor.execute(create_table_query)
# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()
