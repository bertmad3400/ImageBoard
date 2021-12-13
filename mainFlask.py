#!/usr/bin/python3
from flask import Flask, render_template, redirect, url_for, flash, request

import os, random

import json
import csv

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
from wtforms.validators import InputRequired, Length, Optional

app.config['UPLOAD_FOLDER'] = './static/images/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

class UploadForm(FlaskForm):
    title = StringField('Title:', validators=[InputRequired(), Length(max=50, message=('Din besked er for lang. Den skal være mindre end 200 karakterere lang.'))])
    author = StringField("Brugernavn:", validators=[InputRequired(), Length(max=30, message=('Dit brugernavn er for langt. Den skal være mindre end 30 karakterere lang.'))], default="Anon")
    message = TextAreaField('Besked:', validators=[InputRequired(), Length(max=500, message=('Din besked er for lang. Den skal være mindre end 500 karakterere lang.'))])
    imageFile = FileField("Billede:", validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Dit billede skal være af formattet .png, .jpeg, .jpg eller .gif.')])
    submit = SubmitField('Upload')

    def validate(self):
        if not super(UploadForm, self).validate():
            return False
        if self.imageFile.data and len(self.message.data) > 200:
            msg = "Din besked er for lang. Den skal være mindre end 200 karaktere når der er et billede vedhæftet"
            self.message.errors.append(msg)
            return False

        return True


def loadSecretKey():
    if os.path.isfile("./secret.key"):
        app.secret_key = Path("./secret.key").read_text()
    else:
        currentSecretKey = secrets.token_urlsafe(256)
        with os.fdopen(os.open(Path("./secret.key"), os.O_WRONLY | os.O_CREAT, 0o400), 'w') as file:
            file.write(currentSecretKey)
        app.secret_key = currentSecretKey

def saveNewPost(details):
    postContent = [[], []]
    for detailName in ["title", "author", "message", "imageName"]:
        postContent[0].append(detailName)
        postContent[1].append(details[detailName])

    fileName = datetime.now().strftime("%Y!%m!%d-%H:%M:%S.%f") + ".csv"

    with open(f"./static/messages/{fileName}", "w") as msgFile:
        csv.writer(msgFile, delimiter=",").writerows(postContent)

def readPost(fileName):
    with open(f"./static/messages/{fileName}", "r") as msgFile:
        reader = csv.reader(msgFile, delimiter=",")
        detailNames = reader.__next__()
        postContent = reader.__next__()

    return {detailName:postContent[i] for i,detailName in enumerate(detailNames)}


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
