from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


# A Camper has many Activitys through Signups
# An Activity has many Campers through Signups
# A Signup belongs to a Camper and belongs to a Activity

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    #serializer rules
    serialize_only = ('id', 'name', 'age', 'signups')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Relationship to the Signup model
    signups = db.relationship(
        'Signup', back_populates='camper', cascade="all, delete-orphan")

    # Association proxy to access activities directly through camper.activities
    activities = association_proxy('signups', 'activity')

    #validate name
    @validates('name')
    def validate_name(self, key, value):
        if value is not None:
            if value.strip() == '':
                raise ValueError('Camper name cannot be empty')
        return value

    #validate age
    #age between 8 and 18, inclusive


    @validates('age')
    def validate_age(self, key, value):
        if value < 8 or value > 18:
            raise ValueError('Camper age must be between 8 and 18, inclusive')
        return value



    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    serialize_rules = ('-signups.activity', '-camper.activities')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

    # Relationship to the Signup model
    signups = db.relationship(
        'Signup', back_populates='activity', cascade="all, delete-orphan")

    # Association proxy to access campers directly through activity.campers
    campers = association_proxy('signups', 'camper')

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}, Difficulty: {self.difficulty}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    serialize_rules = ('-activity.signups', '-camper.signups')

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, nullable=False)

    # Foreign keys
    camper_id = db.Column(db.Integer, db.ForeignKey(
        'campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey(
        'activities.id'), nullable=False)

    # Relationships to Camper and Activity
    camper = db.relationship('Camper', back_populates='signups')
    activity = db.relationship('Activity', back_populates='signups')

    #validate signnup time
    @validates('time')
    def validate_time(self, key, value):
        if value < 0 or value > 23:
            raise ValueError('Signup time must be between 0 and 23, inclusive')
        return value

    def __repr__(self):
        return f'<Signup {self.id}: Camper {self.camper_id}, Activity {self.activity_id}, Time {self.time}>'
