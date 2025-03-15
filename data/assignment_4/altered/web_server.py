import os
import sqlite3
from bs4 import BeautifulSoup
import pandas as pd

# 📂 Define paths
html_folder = "/Users/kebbaleigh/Library/Mobile Documents/com~apple~CloudDocs/Documents/Education/DATA 304/data_wrangling_304/data/assignment_4/downloaded_class_submissions"
db_folder = "/Users/kebbaleigh/Library/Mobile Documents/com~apple~CloudDocs/Documents/Education/DATA 304/data_wrangling_304/data/assignment_4/altered"
db_output = os.path.join(db_folder, "class_info.sqlite3")

# ✅ Ensure the "altered" folder exists
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# ✅ Connect to SQLite (this will create the database file if it doesn't exist)
conn = sqlite3.connect(db_output)
cursor = conn.cursor()

# ✅ Create tables if they don’t exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        name_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        name_id INTEGER,
        category TEXT,
        favorite TEXT,
        FOREIGN KEY(name_id) REFERENCES students(name_id)
    )
""")

conn.commit()

# ✅ Process HTML files
for filename in os.listdir(html_folder):
    if filename.endswith(".html"):
        file_path = os.path.join(html_folder, filename)
        
        # Open and read the HTML file
        with open(file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract Name from <h1>
        name_tag = soup.find("h1")
        if name_tag:
            name_value = name_tag.text.strip()
            first_name, last_name = name_value.split(" ", 1)  # Split into first and last name
            
            # Insert name into database
            cursor.execute("INSERT OR IGNORE INTO students (first_name, last_name) VALUES (?, ?)", (first_name, last_name))
            cursor.execute("SELECT name_id FROM students WHERE first_name = ? AND last_name = ?", (first_name, last_name))
            name_id = cursor.fetchone()[0]

            # Extract Favorites Table
            table = soup.find("table")
            if table:
                rows = table.find_all("tr")[1:]  # Skip the header row
                for row in rows:
                    cols = [td.text.strip() for td in row.find_all("td")]
                    if len(cols) == 2:  # Ensure there are two columns
                        category, favorite = cols
                        cursor.execute("INSERT INTO favorites (name_id, category, favorite) VALUES (?, ?, ?)", (name_id, category, favorite))

# ✅ Commit changes and close connection
conn.commit()
conn.close()

print(f"✅ Normalized data successfully saved to {db_output}")