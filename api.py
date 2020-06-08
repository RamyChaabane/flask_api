import os
import sys

import markdown
import pymysql
from flask import Flask, request
from flask_restful import Resource, Api

# create a flask instance
flask_app = Flask(__name__)

# create the API
api = Api(flask_app)


@flask_app.route("/")
def index():
    """Present some documentation"""

    # Open the README file
    with open(os.path.dirname(flask_app.root_path) + '/API/README.md', 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)


# connect to database
def mysql_connect():
    connect_params = dict(
        host="192.168.0.24",
        user="root",
        password="",
        db="classicmodels",
        cursorclass=pymysql.cursors.DictCursor
    )
    return pymysql.connect(**connect_params)


class Customers(Resource):

    def __init__(self):
        Resource.__init__(self)
        self._field = {
            'salesRepEmployeeNumber': {"required": True, "type": "int"},
            'addressLine1': {"required": True, "type": "str"},
            'addressLine2': {"required": False, "type": "str"},
            'city': {"required": True, "type": "str"},
            'contactFirstName': {"required": True, "type": "str"},
            'contactLastName': {"required": True, "type": "str"},
            'country': {"required": True, "type": "str"},
            'customerName': {"required": True, "type": "str"},
            'phone': {"required": True, "type": "str"},
            'postalCode': {"required": False, "type": "str"},
            'state': {"required": False, "type": "str"},
        }

    def get(self):
        db = mysql_connect()
        sql_query = "select customerNumber, {} from customers".format(', '.join(self._field.keys()))
        with db.cursor() as cursor:
            cursor.execute(sql_query)
            return cursor.fetchall()

    def post(self):
        _json = request.json

        _type = {"int": int, "str": str}

        request_args = dict()
        for key, value in self._field.iteritems():
            arg = _json[key]

            if not arg and value['required']:
                sys.exit("{} is missing".format(key))

            type_arg = str

            try:
                int(arg)
                type_arg = int
            except ValueError:
                pass
            finally:
                if _type[value["type"]] != type_arg:
                    sys.exit("type of {} is not {}".format(key, value["type"]))

            request_args[key] = arg

        rows = request_args.keys()
        s_rows = "%s, "*(len(rows) - 1) + "%s"

        input_sql_query = "insert into customers ({}) ".format(s_rows) % tuple(rows) + " values ({})".format(s_rows)

        print input_sql_query
        print tuple(request_args.values())

        db = mysql_connect()
        with db.cursor() as cursor:
            cursor.execute(input_sql_query, tuple(request_args.values()))
            request_args['customerNumber'] = cursor.lastrowid
        db.commit()

        return {'message': 'Customer registered', 'data': request_args}, 201


class Customer(Resource):

    def __init__(self):
        Resource.__init__(self)
        self._field = {
            'salesRepEmployeeNumber': {"required": True, "type": "int"},
            'addressLine1': {"required": True, "type": "str"},
            'addressLine2': {"required": False, "type": "str"},
            'city': {"required": True, "type": "str"},
            'contactFirstName': {"required": True, "type": "str"},
            'contactLastName': {"required": True, "type": "str"},
            'country': {"required": True, "type": "str"},
            'customerName': {"required": True, "type": "str"},
            'phone': {"required": True, "type": "str"},
            'postalCode': {"required": False, "type": "str"},
            'state': {"required": False, "type": "str"},
        }

    def get(self, uuid):

        sql_query = "select customerNumber, {rows} from customers where " \
                    "customerNumber='{id}'".format(rows=', '.join(self._field.keys()), id=uuid)

        db = mysql_connect()
        with db.cursor() as cursor:
            cursor.execute(sql_query)
            sql_result = cursor.fetchone()
        db.close()

        if not sql_result:
            return {'message': 'Customer not found'}, 404
        else:
            sql_result['customerNumber'] = uuid
            return {'message': 'Customer found', 'data': sql_result}, 200

    def delete(self, uuid):

        sql_query = "select customerNumber, {rows} from customers where " \
                    "customerNumber='{id}'".format(rows=', '.join(self._field.keys()), id=uuid)

        db = mysql_connect()
        with db.cursor() as cursor:
            cursor.execute(sql_query)
            sql_result = cursor.fetchone()
        db.close()

        if not sql_result:
            return {'message': 'Customer not found'}, 404
        else:
            sql_delete_query = "delete from customers where customerNumber='{}'".format(uuid)

            db = mysql_connect()
            with db.cursor() as cursor:
                cursor.execute(sql_delete_query)
            db.commit()

            return '', 204


api.add_resource(Customers, '/customers')
api.add_resource(Customer, '/customer/<string:uuid>')
