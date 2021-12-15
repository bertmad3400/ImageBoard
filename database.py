import sqlite3

DBName = "BKI.db"

def executeDBCommand(command, paramaters, returnResponse=False):
    conn = sqlite3.connect(DBName)
    cur = conn.cursor()

    cur.execute(command, paramaters)
    if returnResponse:
        DBResults = cur.fetchall()

    conn.commit()
    conn.close()
    if returnResponse:
        return DBResults

def countComments(postID):
    return executeDBCommand("SELECT COUNT(id) FROM comments WHERE post_id=?", (postID,), True)[0][0]

def listPosts(limit=False):
    collumns = "id, title, author, content, image_id"
    command = f"SELECT {collumns} FROM posts ORDER BY id DESC"

    if limit:
        command += f" LIMIT {str(limit)}"

    results = executeDBCommand(command, (), True)

    return [{descriptor:value for (descriptor,value) in zip(collumns.split(", "), result)} for result in results]

def saveNewPost(details):
    executeDBCommand("INSERT INTO posts (title, author, content, image_id) VALUES (?, ?, ?, ?)", (details["title"], details["author"], details["message"], details["imageName"]))


def readPost(postID):
    collumns = "id, title, author, content, image_id"

    result = executeDBCommand(f"SELECT {collumns} FROM posts WHERE id=?", (postID,), True)[0]

    return {descriptor:value for (descriptor,value) in zip(collumns.split(", "), result)}

def readPostComments(postID):
    collumns = "author, content"

    results = executeDBCommand(f"SELECT {collumns} FROM comments WHERE post_id=?", (postID,), True)

    return [{descriptor:value for (descriptor,value) in zip(collumns.split(", "), result)} for result in results]

def commentOnPost(postID, details):
    executeDBCommand("INSERT INTO comments (post_id, author, content) VALUES (?, ?, ?)", (postID, details["author"], details["comment"]))
