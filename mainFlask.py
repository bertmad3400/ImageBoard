#!/usr/bin/python3
from flask import Flask, render_template, redirect, url_for, flash, request

import os, random

import json

import uuid

from pathlib import Path
import secrets

from datetime import datetime

app = Flask(__name__)
app.static_folder = "./static"
app.template_folder = "./templates"

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length

app.config['UPLOAD_FOLDER'] = './static/images/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

class UploadForm(FlaskForm):
    title = StringField('Title:', validators=[InputRequired(), Length(max=50, message=('Din besked er for lang. Den skal være mindre ned 200 karakterere lang.'))])
    author = StringField("Brugernavn:", validators=[InputRequired(), Length(max=30, message=('Dit brugernavn er for langt. Den skal være mindre ned 30 karakterere lang.'))], default="Anon")
    message = TextAreaField('Besked:', validators=[InputRequired(), Length(max=200, message=('Din besked er for lang. Den skal være mindre ned 200 karakterere lang.'))])
    imageFile = FileField("Billede:", validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Dit billede skal være af formattet .png, .jpeg, .jpg eller .gif.')])
    submit = SubmitField('Upload')


def loadSecretKey():
    if os.path.isfile("./secret.key"):
        app.secret_key = Path("./secret.key").read_text()
    else:
        currentSecretKey = secrets.token_urlsafe(256)
        with os.fdopen(os.open(Path("./secret.key"), os.O_WRONLY | os.O_CREAT, 0o400), 'w') as file:
            file.write(currentSecretKey)
        app.secret_key = currentSecretKey


@app.route("/")
def showFeed():
    messagesPath = os.listdir("./static/messages/")
    messagesPath.sort(reverse=True)
    messageList = []

    for messageFile in messagesPath:
        if messageFile.endswith(".json"):
            with open(f"./static/messages/{messageFile}", "r") as messageFileObject:
                messageList.append(json.load(messageFileObject))

    return render_template("feed.html", messageList=messageList)
    

@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        if form.imageFile.data:
            imageName = str(uuid.uuid4()) + "." + form.imageFile.data.filename.rsplit('.', 1)[1].lower()
            form.imageFile.data.save(os.path.join(app.config['UPLOAD_FOLDER'], imageName))
        else:
            imageName = ""

        messageDetails = {"imageName" : imageName, "author" : form.author.data if form.author.data else "", "title" : form.title.data, "message" : form.message.data}
        fileName = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        with open(f"./static/messages/{fileName}.json", "w") as messageFileObject:
            json.dump(messageDetails, messageFileObject)

        flash("Uploaded besked")
        return redirect(url_for("showFeed"))
    else:
        return render_template("upload.html", form=form)

loadSecretKey()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
