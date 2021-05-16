'''
A Flask based API
'''
# pylint: disable=R0201
from flask import Flask, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from picture import id_to_filename, reconcile_images


# Database connection for API
db_connect = create_engine("sqlite:///socialnetwork.db")


class Users(Resource):
    '''
    Class representing the users page on the web server
    '''
    def get(self):
        '''
        Gives the web server User's details and their status information
        '''
        conn = db_connect.connect()
        result = {}
        query = conn.execute('SELECT * FROM User')
        for user in query.cursor:
            user = dict(zip(tuple(query.keys())[1:], user[1:]))
            user_id = user.pop('user_id')
            statuses = conn.execute(f'SELECT status_text FROM Status WHERE user_id = "{user_id}"')
            user['status_updates'] = [status[0] for status in statuses.cursor]
            result[user_id] = user
        conn.close()
        return jsonify(result)


class Images(Resource):
    '''
    Class representing the images page on the web server
    '''
    def get(self):
        '''
        Gives the web server a list of users and their image details
        '''
        conn = db_connect.connect()
        result = {}
        query = conn.execute('SELECT user_id FROM User')
        for user in query.cursor:
            user_id = user[0]
            command = f'SELECT tags, picture_id FROM Picture WHERE user_id = "{user_id}"'
            images = conn.execute(command)
            for values in images.cursor:
                image = dict(zip(tuple(images.keys()), values))
                image['image_name'] = id_to_filename(image.pop("picture_id"))
                try:
                    result[user_id].append(image)
                except KeyError:  # Clause for the first image
                    result[user_id] = [image]
        conn.close()
        return jsonify(result)


class Differences(Resource):
    '''
    Class representing the defferences page on the web server
    '''
    def get(self):
        '''
        Gives the web server any differences between the image directory and the image database
        '''
        conn = db_connect.connect()
        result = {}
        query = conn.execute('SELECT user_id FROM User')
        for user in query.cursor:
            user_id = user[0]
            compare = reconcile_images(user_id)
            if compare:
                result[user_id] = compare
        conn.close()
        return jsonify(result)


def setup(name=__name__):
    '''
    Prepares the app for execution
    '''
    server = Flask(name)
    api = Api(server)
    api.add_resource(Users, "/users")
    api.add_resource(Images, "/images")
    api.add_resource(Differences, "/differences")
    return server


if __name__ == '__main__':
    app = setup()

    app.run(port="5002")

    db_connect.dispose()
