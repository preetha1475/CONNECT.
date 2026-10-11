
import pandas as pd
import mysql.connector

path = r"C:\CONNECT\data\Chennai_neighbourhood_coordintes.csv"

df = pd.read_csv(path, encoding="cp1252")
df.columns = df.columns.str.strip()

# Connect to your existing database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="connect_ngo"
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chennai_neighbourhoods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(150) NOT NULL,
    location VARCHAR(150),
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL
)
""")

count = 0

for _, row in df.iterrows():
    area = str(row["Area"]).strip()

    if not area or area.lower() == "nan":
        continue

    try:
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])
    except (ValueError, TypeError):
        continue

    if not (12.7 <= lat <= 13.3 and 80.0 <= lon <= 80.4):
        continue

    location = str(row.get("Location", "")).strip()
    if location.lower() == "nan":
        location = ""

    # Update an existing area or insert a new one
    cursor.execute(
        "SELECT id FROM chennai_neighbourhoods WHERE area=%s LIMIT 1",
        (area,)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE chennai_neighbourhoods
            SET location=%s, latitude=%s, longitude=%s
            WHERE id=%s
        """, (location, lat, lon, existing[0]))
    else:
        cursor.execute("""
            INSERT INTO chennai_neighbourhoods
            (area, location, latitude, longitude)
            VALUES (%s, %s, %s, %s)
        """, (area, location, lat, lon))

    count += 1

conn.commit()

cursor.execute("SELECT COUNT(*) FROM chennai_neighbourhoods")
print("Areas in database:", cursor.fetchone()[0])
print("CSV area records processed:", count)

cursor.close()
conn.close()
