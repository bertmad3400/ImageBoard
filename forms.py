from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

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

class CommentForm(FlaskForm):
    author = StringField("Brugernavn:", validators=[InputRequired(), Length(max=30, message=('Dit brugernavn er for langt. Den skal være mindre end 30 karakterere lang.'))], default="Anon")
    comment = TextAreaField('Kommentar:', validators=[InputRequired(), Length(max=200, message=('Din kommentar er for lang. Den skal være mindre end 200 karakterere lang.'))])
    submit = SubmitField('Kommenter')
