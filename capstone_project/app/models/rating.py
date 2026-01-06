from datetime import datetime
from ..extensions import db

class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    matatu_id = db.Column(db.Integer, db.ForeignKey("matatus.id"), nullable=False)

    score = db.Column(db.Integer, nullable=False)  # 1–5
    comment = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        if self.score < 1 or self.score > 5:
            raise ValueError("Rating must be between 1 and 5")
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "matatu_id": self.matatu_id,
            "score": self.score,
            "comment": self.comment,
            "created_at": self.created_at.isoformat()
        }
