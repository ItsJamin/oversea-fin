from . import db


class ExampleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
