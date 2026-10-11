
import json
import urllib.request
import urllib.parse
import urllib.error
import time
import mysql.connector

# Smaller Chennai-area sections
boxes = [
    (12.7, 80.0, 13.0, 80.2),
    (12.7, 80.2, 13.0, 80.4),
    (13.0, 80.0, 13.15, 80.2),
    (13.0, 80.2, 13.15, 80.4),
    (13.15, 80.0, 13.3, 80.2),
    (13.15, 80.2, 13.3, 80.4),
]

endpoints = [
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="connect_ngo"
)
cursor = conn.cursor()

cursor.execute("""
    SELECT facility_name, latitude, longitude
    FROM healthcare_facilities
""")
existing = {
    (n, round(float(lat), 6), round(float(lon), 6))
    for n, lat, lon in cursor.fetchall()
}

added = 0
seen = set()

for i, (south, west, north, east) in enumerate(boxes, start=1):
    print(f"\nArea {i}/{len(boxes)}")

    query = f"""
    [out:json][timeout:25];
    (
      nwr["amenity"~"hospital|clinic|doctors"]
        ({south},{west},{north},{east});
      nwr["healthcare"~"hospital|clinic|doctor|centre|health_post"]
        ({south},{west},{north},{east});
    );
    out center tags;
    """

    data = None

    for endpoint in endpoints:
        try:
            req = urllib.request.Request(
                endpoint,
                data=urllib.parse.urlencode({"data": query}).encode(),
                headers={"User-Agent": "CONNECT-NGO-Map/1.0"}
            )

            with urllib.request.urlopen(req, timeout=40) as response:
                data = json.loads(response.read().decode())

            print("Retrieved:", len(data.get("elements", [])))
            break

        except Exception as error:
            print("Endpoint unavailable:", endpoint, error)

    if data is None:
        print("Skipping this area; all endpoints failed.")
        continue

    for item in data.get("elements", []):
        tags = item.get("tags", {})
        name = tags.get("name", "").strip()

        if not name:
            continue

        loc = item.get("center", item)

        if "lat" not in loc or "lon" not in loc:
            continue

        lat = float(loc["lat"])
        lon = float(loc["lon"])

        if not (12.7 <= lat <= 13.3 and 80.0 <= lon <= 80.4):
            continue

        key = (name, round(lat, 6), round(lon, 6))

        if key in existing or key in seen:
            continue

        category = (
            tags.get("amenity")
            or tags.get("healthcare")
            or "healthcare facility"
        )

        area = (
            tags.get("addr:suburb")
            or tags.get("addr:neighbourhood")
            or ""
        )

        cursor.execute("""
            INSERT INTO healthcare_facilities
            (facility_name, facility_type, area,
             latitude, longitude, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, category, area, lat, lon, "OpenStreetMap"))

        seen.add(key)
        added += 1

    conn.commit()
    time.sleep(1)

cursor.execute("SELECT COUNT(*) FROM healthcare_facilities")
total = cursor.fetchone()[0]

print("\nNew locations added:", added)
print("Total database locations:", total)

cursor.close()
conn.close()
