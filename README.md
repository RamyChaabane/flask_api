# Introduction
Building a REST API with Flask and MySQL storing customers

# What you can do
Collection:
+ GET: get all customers stored in the database
+ POST: add a customer and store it in the database

Resource:
+ GET: get a customer by uuid or name
+ PUT: update a customer by uuid or name
+ DELETE: delete a customer by uuid or name

If multiple customers share the same name a conflict exception will be raised

# Get started
- install git, docker, and docker-compose
- clone the repo: git clone https://github.com/RamyChaabane/flask_api.git
- change directory to flask_api
- docker-compose up

# Test the API  
- Get customers: curl http://<docker_host_ip>/customers
- Add a customer: curl "http://<docker_host_ip>/customers" -X POST -d "<data_in_json_format>" -H "Content-Type: application/json"  
some mandatory data need to be provided  

````
{
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
````

_**Example:**_
````  
{           
    "salesRepEmployeeNumber": 6,  
    "addressLine1": "Champs Elysée",
    "addressLine2": "",
    "city": "Paris",
    "contactFirstName": "test",
    "contactLastName": "test",
    "country": "France",
    "customerName": "Apple",
    "phone": "+33xxxxxxxxx",
    "postalCode": 75008,
    "state": "",
}
````
- Get customer by uuid: curl http://<docker_host_ip>/customer/<uuid>
- Get customer by name: curl http://<docker_host_ip>/customer/<name>
- Delete a customer: curl "http://<docker_host_ip>/customer/<name_or_uuid>" -X DELETE
- Update a customer: curl "http://<docker_host_ip>/customer/<name_or_uuid>" -X PUT -d <data_in_json_format> -H "Content-Type: application/json"
