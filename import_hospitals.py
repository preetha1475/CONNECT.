
import pandas as pd
import mysql.connector

CSV_PATH = r"C:\CONNECT\data\hospital_directory.csv"

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="connect_ngo"
)

cursor = conn.cursor()

# Read CSV
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()

# Filter Chennai hospitals
df["State"] = df["State"].fillna("").astype(str)
df["District"] = df["District"].fillna("").astype(str)

df = df[
    df["State"].str.contains("Tamil Nadu", case=False)
    & df["District"].str.contains("Chennai", case=False)
].copy()

# Extract coordinates
coords = df["Location_Coordinates"].fillna("").astype(str).str.split(",", expand=True)

if coords.shape[1] >= 2:
    df["latitude"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
    df["longitude"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")
else:
    df["latitude"] = pd.NA
    df["longitude"] = pd.NA

# Keep only valid Chennai coordinates and hospital names
df["Hospital_Name"] = df["Hospital_Name"].fillna("").astype(str).str.strip()

df = df[
    df["Hospital_Name"].ne("")
    & df["latitude"].between(12.7, 13.3)
    & df["longitude"].between(80.0, 80.4)
].copy()

# Bulk insert
records = []

for _, row in df.iterrows():
    category = str(row.get("Hospital_Care_Type", "") or "").strip()
    area = str(row.get("Location", "") or "").strip()

    records.append((
        row["Hospital_Name"],
        category if category.lower() != "nan" else "",
        area if area.lower() != "nan" else "",
        float(row["latitude"]),
        float(row["longitude"]),
        "hospital_directory.csv"
    ))

if records:
    cursor.executemany("""
        INSERT INTO healthcare_facilities
        (facility_name, facility_type, area, latitude, longitude, source)
        SELECT %s, %s, %s, %s, %s, %s
        FROM DUAL
        WHERE NOT EXISTS (
            SELECT 1 FROM healthcare_facilities h
            WHERE h.facility_name = %s
              AND h.latitude = %s
              AND h.longitude = %s
        )
    """, [
        r + (r[0], r[3], r[4])
        for r in records
    ])

    conn.commit()

print("Chennai hospitals checked:", len(records))
print("Valid-coordinate records were processed.")
print("Check MySQL for the actual inserted count.")

cursor.close()
conn.close()
