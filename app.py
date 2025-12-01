from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# --- Flask setup ---
app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Firebase setup ---
cred = credentials.Certificate("C:/AIoT/Server/Firebase/smart-parking.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Admin credentials ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Tên đăng nhập hoặc mật khẩu sai!")
    return render_template("login.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    logs = []
    if request.method == "POST":
        license_plate = request.form.get("license_plate")
        type_filter = request.form.get("type")
        caution_filter = request.form.get("caution")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")

        query = db.collection("Logs")

        if license_plate:
            query = query.where("license_plate", "==", license_plate)
        if type_filter and type_filter != "all":
            query = query.where("type", "==", type_filter)
        if caution_filter and caution_filter != "all":
            query = query.where("caution", "==", caution_filter)
        if start_time:
            dt_start = datetime.fromisoformat(start_time)
            query = query.where("time", ">=", dt_start)
        if end_time:
            dt_end = datetime.fromisoformat(end_time)
            query = query.where("time", "<=", dt_end)

        results = query.stream()
        for r in results:
            log = r.to_dict()
            logs.append(log)

    return render_template("dashboard.html", logs=logs)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
