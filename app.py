from flask import Flask, render_template, request, redirect, session
from db import engine, Base, Sessionlocal
from werkzeug.security import generate_password_hash, check_password_hash
import models
import PyPDF2
import docx
import json
from ai import analyze_resume
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import os
import dotenv

app = Flask(__name__)
app.secret_key = "secret123"
Base.metadata.create_all(bind=engine)

app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)

#HOME
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")
#Signup
@app.route("/signup", methods=["GET", "POST"])
def signup():
    db = Sessionlocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            return "User already exists"
        hashed = generate_password_hash(password)

        user = models.User(
        email=email,
        password=hashed
)
        db.add(user)
        db.commit()
        db.close()
        return redirect("/login")
    return render_template("signup.html")
#Login
@app.route("/login", methods=["GET", "POST"])
def login():
    db = Sessionlocal()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.query(models.User).filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
           session["user"] = user.email
           return redirect("/dashboard")
        else:
           return "Invalid Credentials"

        if user and check_password_hash(user.password, password):
            session["user"] = user.email
            return redirect("/dashboard")

            return "Invalid Credentials"
                                               
        if user:
            session["user"] = user.email
            return redirect("/dashboard")
            
        else:
            return "Invalid Credentials"
        db.close()

    return render_template("login.html")
#Forgot Password
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email")

        db = Sessionlocal()

        user = db.query(models.User).filter_by(email=email).first()

        if user:

            token = serializer.dumps(email, salt="password-reset")

            reset_link = request.host_url + "reset-password/" + token

            msg = Message(
                "Password Reset",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )

            msg.body = f"""
Click the link below to reset your password.

{reset_link}

This link expires in 30 minutes.
"""

            mail.send(msg)

            return "Password reset link sent."

        return "Email not found."

    return render_template("forgot_password.html")
#Reset Password
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:
        email = serializer.loads(
            token,
            salt="password-reset",
            max_age=1800
        )

    except:
        return "Invalid or expired link."

    if request.method == "POST":

        new_password = request.form.get("password")

        hashed = generate_password_hash(new_password)

        db = Sessionlocal()

        user = db.query(models.User).filter_by(email=email).first()

        user.password = hashed

        db.commit()

        return redirect("/login")

    return render_template("reset_password.html")
#Dashboard
@app.route("/dashboard" , methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")
    
    result = None
    if request.method == "POST":
        user_goal= request.form.get("role")
        resume_text = request.form.get("resume")
        file = request.files.get("file")
#file handling
        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text="" 
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                        resume_text = text
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}
            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text=""
                    for para in doc.paragraphs:
                        text += para.text +"\n"
                        resume_text = text
                except Exception as e:
                    result = {"error": f"DOCX error: {str(e)}"}
        if resume_text and user_goal:
            try:
                result = analyze_resume(resume_text, user_goal)

                #save to db
                db= Sessionlocal()
                user= db.query(models.User).filter_by(email=session["user"]).first()

                report = models.Reports(
                    user_id=user.id, 
                    resume_text=resume_text, 
                    result= json.dumps(result)
                    )
                db.add(report)
                db.commit()
                db.close()

            except Exception as e:
                result = {"error": f"AI Error: {str(e)}"}
    return render_template("dashboard.html",
                                user=session["user"],
                                result=result
                                )            
    print("POST request received")
    print("Role:", user_goal)
    print("Resume length:", len(resume_text) if resume_text else 0)
    print("File:", file.filename if file else "No file")
    print("Calling analyze_resume()")
    #History
@app.route("/history", methods=["GET", "POST"])
def history():
       if "user" not in session:
           return redirect("/login")
       
       db = Sessionlocal()
       user = db.query(models.User).filter_by(email=session["user"]).first()

       reports = db.query(models.Reports).filter_by(user_id=user.id).all()

       #convert JSON string > dict
       parsed_reports = []

       for r in reports:
            try:
             result = json.loads(r.result)
            except json.JSONDecodeError:
             result = {}

            parsed_reports.append({
            "resume": r.resume_text,
             "result": result
    })
           
       return render_template("history.html", reports=parsed_reports)
#Logout
@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    return redirect("/login")
if __name__ == "__main__":
    app.run(debug=True)
    