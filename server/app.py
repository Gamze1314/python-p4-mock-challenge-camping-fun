#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''


class Campers(Resource):
    def get(self):
        campers = Camper.query.all()

        camper_serialized = [camper.to_dict(
            only=('id', 'name', 'age')) for camper in campers]

        return make_response(jsonify(camper_serialized), 200)

# POST request to /campers ; should create a new camper
# body of request {
#   "name": "Zoe",
#   "age": 11
# }

    def post(self):
        try:
            data = request.get_json()
            name = data.get('name')
            age = data.get('age')

            camper = Camper(name=name, age=age)
            db.session.add(camper)
            db.session.commit()

            response_body = camper.to_dict(only=('id', 'name', 'age'))

            return make_response(response_body, 201)

        except Exception as e:
            # Log the error for debugging
            print(f"Error: {e}")
            return {"errors": ["Validation errors"]}, 400


api.add_resource(Campers, '/campers')


class CamperByID(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            return make_response(camper.to_dict(), 200)
        else:
            return {'error': 'Camper not found'}, 404

    def patch(self, id):
        # Updates campers with PATCH requests to /campers/<int:id>
        camper = Camper.query.filter(Camper.id == id).first()

        if camper:
            name = request.json.get('name')
            age = request.json.get('age')

            # Validate the name: it should not be empty
            if name is not None:
                if name.strip() == '':
                    return {"errors": ["validation errors"]}, 400
                camper.name = name + " (updated)"

                # Update the age if it's provided
            if age is not None:
                if age < 8 or age > 18:
                    return {"errors": ["validation errors"]}, 400
                camper.age = age

                db.session.add(camper)
                db.session.commit()

                return make_response(camper.to_dict(only=('id', 'name', 'age')), 202)

        return {"error": "Camper not found"}, 404


api.add_resource(CamperByID, '/campers/<int:id>')


# add patch request handler. /campers/id
# post campers
# get activities

class Activities(Resource):
    def get(self):
        activities = Activity.query.all()

        activity_serialized = [activity.to_dict(
            only=('id', 'name', 'difficulty')) for activity in activities]

        return make_response(jsonify(activity_serialized), 200)


api.add_resource(Activities, '/activities')


class ActivityByID(Resource):
    # def get(self, id):

    #     activity = Activity.query.filter_by(id=id).first()

    #     if activity:
    #         return make_response(activity.to_dict(only=('id', 'name', 'difficulty')), 204)

    #     return {"error": "Activity not found"}, 404

    def delete(self, activity_id):
        activity = Activity.query.get(activity_id)

        if activity:
            # Delete associated signups
            Signup.query.filter_by(activity_id=activity_id).delete()

            # Delete the activity
            db.session.delete(activity)
            db.session.commit()

            return '', 204
        else:
            return {"error": "Activity not found"}, 404


api.add_resource(ActivityByID, '/activities/<int:activity_id>')


# post signups

class Signups(Resource):

    def get(self):
        signups = Signup.query.all()

        signup_serialized = [signup.to_dict() for signup in signups]

        return make_response(jsonify(signup_serialized), 200)

    def post(self):
        try:
            data = request.get_json()
            camper_id = data.get('camper_id')
            activity_id = data.get('activity_id')
            time = data.get('time')

            signup = Signup(camper_id=camper_id,
                            activity_id=activity_id, time=time)
            db.session.add(signup)
            db.session.commit()

            response_body = signup.to_dict()

            return make_response(response_body, 201)

        except:
            return {'errors': ["validation errors"]}, 400


api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
