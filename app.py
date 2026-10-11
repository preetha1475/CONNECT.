
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection

app = Flask(__name__)
app.secret_key = "change-this-before-deployment"

@app.route("/")
def index():
    return redirect(url_for("intro_page"))


def query_database(sql, values=(), fetch=False):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(sql, values)

        if fetch:
            return cursor.fetchall()

        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()

        
@app.route("/intro")
def intro_page():
    return render_template("index1.html")

@app.route("/home")
def home():
    return render_template("index.html")




@app.route("/needs", methods=["GET", "POST"])
def needs_page():
    if request.method == "POST":
        ngo_id = request.form.get("ngo_id", type=int)
        need_type = request.form.get("need_type", "").strip()
        description = request.form.get("description", "").strip()
        area = request.form.get("area", "").strip()
        urgency = request.form.get("urgency", "Medium").strip()

        if not ngo_id or not all([need_type, description, area]):
            flash("Please select an NGO and fill in all required fields.")
            return redirect(url_for("needs_page"))

        # Get the selected NGO's name from MySQL
        selected_ngo = query_database("""
            SELECT name FROM ngos WHERE id = %s
        """, (ngo_id,), fetch=True)

        if not selected_ngo:
            flash("Please select a valid NGO.")
            return redirect(url_for("needs_page"))

        ngo_name = selected_ngo[0]["name"]

        # Save the request in the existing ngo_needs table
        query_database("""
            INSERT INTO ngo_needs
                (ngo_name, need_type, description, area, status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """, (ngo_name, need_type, description, area))

        flash("NGO need saved successfully!")
        return redirect(url_for("needs_page"))

    ngos = query_database("""
        SELECT id, name, registration_no,
               district_state, address, sectors
        FROM ngos
        ORDER BY name
    """, fetch=True)

    records = query_database("""
        SELECT ngo_name, need_type, description, area, status
        FROM ngo_needs
        ORDER BY id DESC
    """, fetch=True)

    return render_template(
        "needs.html",
        ngos=ngos,
        records=records,
        selected_ngo_id=request.args.get("ngo_id", type=int)
    )




@app.route("/food", methods=["GET", "POST"])
def food():
    if request.method == "POST":
        donor = request.form.get("donor_name", "").strip()
        food_name = request.form.get("food_name", "").strip()
        quantity = request.form.get("quantity", "").strip()
        area = request.form.get("area", "").strip()

        if not all([donor, food_name, quantity, area]):
            flash("Please fill in every field.")
        else:
            query_database(
                """INSERT INTO food_donations
                (donor_name, food_name, quantity, area)
                VALUES (%s, %s, %s, %s)""",
                (donor, food_name, quantity, area)
            )
            flash("Food donation saved successfully!")

        return redirect(url_for("food"))

    records = query_database(
        "SELECT * FROM food_donations ORDER BY id DESC", fetch=True
    )
    return render_template("food.html", records=records)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, message]) or "@" not in email:
            flash("Enter a valid email and complete all fields.")
        else:
            query_database(
                """INSERT INTO contact_messages
                (name, email, message)
                VALUES (%s, %s, %s)""",
                (name, email, message)
            )
            flash("Your message has been saved!")

        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/dashboard")
def dashboard():
    needs_total = query_database(
        "SELECT COUNT(*) AS total FROM ngo_needs", fetch=True
    )[0]["total"]

    food_total = query_database(
        "SELECT COUNT(*) AS total FROM food_donations", fetch=True
    )[0]["total"]

    pending_total = query_database(
        """SELECT COUNT(*) AS total FROM ngo_needs
        WHERE status = 'Pending'""", fetch=True
    )[0]["total"]

    available_food = query_database(
        """SELECT COUNT(*) AS total FROM food_donations
        WHERE status = 'Available'""", fetch=True
    )[0]["total"]

    return render_template(
        "dashboard.html",
        needs_total=needs_total,
        food_total=food_total,
        pending_total=pending_total,
        available_food=available_food
    )


@app.route("/map")
def map_page():
    facilities = query_database("""
        SELECT facility_name, facility_type, area,
               latitude, longitude, source
        FROM healthcare_facilities
        WHERE latitude BETWEEN 12.7 AND 13.3
          AND longitude BETWEEN 80.0 AND 80.4
    """, fetch=True)

    neighbourhoods = query_database("""
        SELECT area, location, latitude, longitude
        FROM chennai_neighbourhoods
        WHERE latitude BETWEEN 12.7 AND 13.3
          AND longitude BETWEEN 80.0 AND 80.4
        ORDER BY area
    """, fetch=True)

    for f in facilities:
        f["latitude"] = float(f["latitude"])
        f["longitude"] = float(f["longitude"])

    for n in neighbourhoods:
        n["latitude"] = float(n["latitude"])
        n["longitude"] = float(n["longitude"])

    return render_template(
        "map.html",
        facilities=facilities,
        neighbourhoods=neighbourhoods
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(500)
def server_error(error):
    return (
        "A server or database error occurred. "
        "Check the Command Prompt for details.",
        500
    )


if __name__ == "__main__":
    app.run(debug=True)
