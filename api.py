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
    with open('{}/README.md'.format(os.getcwd()), 'r') as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        return markdown.markdown(content)


# connect to database
class MySQL:
    def __init__(self):
        connect_params = dict(
            host="mysql",
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASS"],
            db=os.environ["MYSQL_DATABASE"],
            cursorclass=pymysql.cursors.DictCursor
        )
        self._db = pymysql.connect(**connect_params)

    def execute(self, sql_query, params=None, fetchone=False):
        with self._db.cursor() as cursor:
            cursor.execute(sql_query, params)
            sql_result, last_id = cursor.fetchone() if fetchone else cursor.fetchall(), cursor.lastrowid

        return sql_result, last_id

    def commit(self):
        return self._db.commit()


class Common(Resource):

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
            'postalCode': {"required": False, "type": "int"},
            'state': {"required": False, "type": "str"},
        }
        self._db = MySQL()


class Customers(Common):

    def get(self):
        sql_query = "select customerNumber, {} from customers".format(', '.join(self._field.keys()))
        sql_result, _ = self._db.execute(sql_query)
        return {'message': 'Success', 'data': sql_result}, 200

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

        _, last_rowid = self._db.execute(input_sql_query, tuple(request_args.values()))
        self._db.commit()
        request_args['customerNumber'] = last_rowid

        return {'message': 'Customer registered', 'data': request_args}, 201


class Customer(Common):

    def get(self, name_or_uuid):

        rows_name = ', '.join(self._field.keys())
        query = "select customerNumber, {rows} from customers where " \
                "(**)='{name_or_uuid}'".format(rows=rows_name, name_or_uuid=name_or_uuid)
        query = query.replace("(**)", "{}")
        try:
            int(name_or_uuid)
            sql_query = query.format("customerNumber")
            print sql_query
            sql_result, _ = self._db.execute(sql_query)
        except ValueError:
            sql_query = query.format("customerName")
            sql_result, _ = self._db.execute(sql_query)

        if not sql_result:
            return {'message': 'Customer not found'}, 404
        else:
            return {'message': 'Customer found', 'data': sql_result}, 200

    def delete(self, name_or_uuid):

        dict_msg, response = self.get(name_or_uuid)
        sql_result = dict_msg.get('data')

        if not sql_result:
            return {'message': 'Customer not found'}, 404
        elif len(sql_result) > 1:
            return {'message': 'more than one customer has the name {}'.format(name_or_uuid)}, 409
        else:
            sql_delete_query = "delete from customers where {}='{}'"
            try:
                int(name_or_uuid)
                sql_delete_query = sql_delete_query.format("customerNumber", name_or_uuid)
            except ValueError:
                sql_delete_query = sql_delete_query.format("customerName", name_or_uuid)
            finally:
                self._db.execute(sql_delete_query)
                self._db.commit()

            return '', 204

    def put(self, name_or_uuid):
        dict_msg, response = self.get(name_or_uuid)
        sql_result = dict_msg['data']

        if not sql_result:
            return {'message': 'Customer not found'}, 404
        elif len(sql_result) > 1:
            return {'message': 'more than one customer has the name {}'.format(name_or_uuid)}, 409
        else:

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

            set_values = ", ".join(["{}='{}'".format(arg_key, arg_value)
                                    for arg_key, arg_value in request_args.iteritems()])

            sql_query = "update customers set {} where (**)='{}'".format(set_values, name_or_uuid)
            sql_query = sql_query.replace("(**)", "{}")
            try:
                int(name_or_uuid)
                sql_query = sql_query.format("customerNumber")
            except ValueError:
                sql_query = sql_query.format("customerName")
            finally:
                self._db.execute(sql_query)
                self._db.commit()

        return '', 204


api.add_resource(Customers, '/customers')
api.add_resource(Customer, '/customer/<string:name_or_uuid>')