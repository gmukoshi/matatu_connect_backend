from ..extensions import db

class Matatu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True)
    capacity = db.Column(db.Integer)
    driver_id = db.Column(db.Integer, db.ForeignKey("user.id"))


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def to_dict(self):
        return{
            "id":self.id,
            "plate_number":self.plate_number,
            "capacity":self.capacity,
            "driver_id":self.driver_id

        }