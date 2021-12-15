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

app.config['UPLOAD_FOLDER'] = './static/images/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

allowedIPs = ["80.164.71.56", "195.249.78.90", "127.0.0.1"]

from database import countComments, listPosts, saveNewPost, readPost, readPostComments, commentOnPost

from forms import UploadForm, CommentForm

def loadSecretKey():
    if os.path.isfile("./secret.key"):
        app.secret_key = Path("./secret.key").read_text()
    else:
        currentSecretKey = secrets.token_urlsafe(256)
        with os.fdopen(os.open(Path("./secret.key"), os.O_WRONLY | os.O_CREAT, 0o400), 'w') as file:
            file.write(currentSecretKey)
        app.secret_key = currentSecretKey

@app.before_request
def checkIP():
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    if request.environ.get('HTTP_X_REAL_IP', request.remote_addr) not in allowedIPs:
        return render_template("accessDenied.html")

@app.route("/")
def showFeed():

    posts = listPosts()

    for post in posts:
        commentCount = countComments(post["id"])
        post["commentCount"] = commentCount if commentCount else 0

    return render_template("feed.html", messageList=posts)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    form = UploadForm()

    if form.validate_on_submit():
        if form.imageFile.data:

            imageName = str(uuid.uuid4()) + "." + form.imageFile.data.filename.rsplit('.', 1)[1].lower()
            form.imageFile.data.save(os.path.join(app.config['UPLOAD_FOLDER'], imageName))
        else:
            imageName = None

        messageDetails = {"imageName" : imageName, "author" : form.author.data, "title" : form.title.data, "message" : form.message.data}
        fileName = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        saveNewPost(messageDetails)

        flash("Uploaded besked")
        return redirect(url_for("showFeed"))
    else:
        return render_template("upload.html", form=form)

@app.route("/post/<int:postID>/", methods=["GET", "POST"])
def renderPost(postID):
    form = CommentForm()
    if form.validate_on_submit():
        commentDetails = {"author" : form.author.data, "comment" : form.comment.data}
        commentOnPost(postID, commentDetails)

        flash("Kommenterede på post")
        return redirect(url_for("renderPost", postID=postID))

    else:
        try:
            post = readPost(postID)
            comments = readPostComments(post["id"])
        except IndexError:
            return redirect(url_for("showFeed"))
        return render_template("post.html", post=post, comments=comments, form=form)

loadSecretKey()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
