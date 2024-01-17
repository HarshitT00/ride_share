from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256
import os
from flask import (
    Flask,
    session,
    render_template,
    request,
    redirect,
    url_for
)

load_dotenv()
def create_app():
    app = Flask(__name__)
    uri = os.getenv("MONGODB_URI")
    client = MongoClient(uri)
    app.db = client.userdb
    app.db1 = client.ridedb
    app.db2 = client.feedbackdb

    app.secret_key = "qwertyuiop"

    # route for home page
    @app.route("/")
    def home():
        session.clear()
        return render_template("home.html")

    # route after successful login
    @app.route("/logedin", methods=["GET", "POST"])
    def logedin():
        email = session.get("email")
        x = app.db.users.find_one({"email": email})
        name = x["name"]
        if request.method == "POST":
            return redirect(url_for("addride"))
        return render_template("logedin.html", name=name)

    # route to add ride after login
    @app.route("/logedin/addride", methods=["GET", "POST"])
    def addride():
        email = session.get("email")
        if request.method == "POST":
            tripID = request.form.get("tripID")
            driverName = request.form.get("driverName")
            phone = request.form.get("phone")
            cabNumber = request.form.get("cabNumber")
            app.db1.rides.insert_one({"email":email, "tripID":tripID, "driverName":driverName, "phone":phone, "cabNumber":cabNumber,})
            return redirect(url_for("logedin"))
        return render_template("addride.html")

    # route to view previous rides
    @app.route("/logedin/history", methods=["GET", "POST"])
    def history():
        email = session.get("email")
        entries = [
                (
                    entry["tripID"],
                    entry["driverName"],
                    entry["phone"],
                    entry["cabNumber"],
                    email
                )
                for entry in app.db1.rides.find({"email": email})
        ]
        return render_template("history.html", entries=entries)

    # route after successful admin login
    @app.route("/adminlogedin")
    def adminlogedin():
        entries = [
                (
                    entry["tripID"],
                    entry["driverName"],
                    entry["phone"],
                    entry["cabNumber"]
                )
                for entry in app.db1.rides.find()
        ]
        return render_template("adminlogedin.html", entries=entries)

    # orute for admin login
    @app.route("/adminlogin", methods=["GET", "POST"])
    def adminlogin():
        message = ""
        if request.method == "POST" :
            email = request.form.get("email")
            password = request.form.get("password")
            corrpassword = "123456789"
            corremail = "admin@1234"
            if password == corrpassword and email==corremail :
                return redirect(url_for("adminlogedin"))
            message = "wrong credentials!"    
        return render_template("adminlogin.html", message=message)

    # route for user login
    @app.route("/login", methods=["GET", "POST"])
    def login():
        session.clear()
        message = ""
        if request.method == "POST" :
            email = request.form.get("email")
            password = request.form.get("password")
            x = app.db.users.find_one({"email": email})
            corrpassword = x["password"]
            if pbkdf2_sha256.verify(password, corrpassword) :
                session["email"] = email
                return redirect(url_for("logedin"))
            message = "wrong credentials!"    
        return render_template("login.html", message=message)

    #route for user login
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST" :
            email = request.form.get("email")
            name = request.form.get("name")
            password = pbkdf2_sha256.hash(request.form.get("password"))

            app.db.users.insert_one({"name": name, "email":email, "password": password}) 
            return redirect(url_for("login"))

        return render_template("register.html")
    
    # route for feedback submit
    @app.route("/logedin/feedback", methods=["GET", "POST"])
    def feedback():
        tripID = request.form.get("tripID")
        email = request.form.get("email")
        if request.method == "POST" :
            return render_template("feedback.html", email=email, tripID=tripID)

    # routte for feedback adding to db    
    @app.route("/logedin/feedback/submit", methods=["GET", "POST"])
    def feedbacksubmit():
        tripID = request.form.get("tripID")
        email = request.form.get("email")
        feedback = request.form.get("feedback")
        app.db2.feedbacks.insert_one({"tripID": tripID, "email":email, "feedback": feedback}) 
        if request.method == "POST" :
            return redirect(url_for("logedin"))
        
    return app

