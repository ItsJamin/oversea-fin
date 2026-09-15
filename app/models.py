from datetime import datetime

from . import db


class Medium(db.Model):
    __tablename__ = "media"

    id = db.Column(db.String(64), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    year = db.Column(db.Integer)
    type = db.Column(db.String(16), nullable=False)
    poster_url = db.Column( db.String(512))
    tmdb_id = db.Column(db.String(64))
    imdb_id = db.Column(db.String(64))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # json array wich contains server-ids
    jellyfin_servers = db.Column(db.String(512))

    def __repr__(self):
        return f"<Medium {self.title} ({self.year})>"
