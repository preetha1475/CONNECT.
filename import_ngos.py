
import pandas as pd
from database import get_connection

# Change this if your CSV filename is different
FILE_PATH = r"C:\CONNECT\data\ngo_list.csv"


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_column(column):
    return "".join(
        ch.lower()
        for ch in str(column)
        if ch.isalnum()
    )


conn = None
cursor = None

try:
    # Read CSV; try common Windows encodings if needed
    try:
        df = pd.read_csv(FILE_PATH, encoding="utf-8-sig", dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(FILE_PATH, encoding="cp1252", dtype=str)

    df.columns = [str(col).strip() for col in df.columns]

    print("CSV columns found:")
    print(df.columns.tolist())
    print("CSV rows found:", len(df))

    columns = {
        normalize_column(col): col
        for col in df.columns
    }

    def find_column(names):
        for name in names:
            if name in columns:
                return columns[name]
        return None

    sr_col = find_column(["srno", "serialno", "sno"])
    name_col = find_column(["nameofnpo", "ngoname", "name"])
    reg_col = find_column([
        "registrationnodistrictstate",
        "registrationno",
        "registrationnumber"
    ])
    district_col = find_column(["districtstate", "district"])
    address_col = find_column(["address", "ngoaddress"])
    sectors_col = find_column([
        "sectorsworkingin",
        "sectorsworking",
        "sectors",
        "sector"
    ])

    if not name_col or not reg_col or not address_col or not sectors_col:
        raise ValueError(
            "Required columns were not found. "
            "Compare the printed CSV columns with the expected headings."
        )

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    updated = 0
    skipped = 0

    for _, row in df.iterrows():
        name = clean_text(row[name_col])

        if not name:
            skipped += 1
            continue

        sr_text = clean_text(row[sr_col]) if sr_col else ""
        try:
            sr_no = int(float(sr_text)) if sr_text else None
        except ValueError:
            sr_no = None

        registration_text = clean_text(row[reg_col])
        parts = [
            part.strip()
            for part in registration_text.splitlines()
            if part.strip()
        ]

        registration_no = parts[0] if parts else ""
        district_state = " ".join(parts[1:])

        if district_col:
            district_state = clean_text(row[district_col])

        address = clean_text(row[address_col])
        sectors = clean_text(row[sectors_col])

        cursor.execute("""
            SELECT id FROM ngos
            WHERE name = %s
              AND registration_no <=> %s
            LIMIT 1
        """, (name, registration_no or None))

        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE ngos
                SET sr_no = %s,
                    registration_no = %s,
                    district_state = %s,
                    address = %s,
                    sectors = %s
                WHERE id = %s
            """, (
                sr_no,
                registration_no or None,
                district_state or None,
                address or None,
                sectors or None,
                existing[0]
            ))
            updated += 1
        else:
            cursor.execute("""
                INSERT INTO ngos
                (sr_no, name, registration_no,
                 district_state, address, sectors)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                sr_no,
                name,
                registration_no or None,
                district_state or None,
                address or None,
                sectors or None
            ))
            inserted += 1

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM ngos")
    total = cursor.fetchone()[0]

    print("\nNGO CSV import completed!")
    print("New NGOs added:", inserted)
    print("Existing NGOs updated:", updated)
    print("Rows skipped:", skipped)
    print("Total NGOs in database:", total)

except Exception as error:
    if conn:
        conn.rollback()
    print("\nIMPORT ERROR:", error)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
