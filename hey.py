import requests
import json

def GET():
	name=raw_input("Enter the name u want to search for: ")
	uri= "http://localhost:8081/mainhand"
	payload={"name":name}
	r = requests.get(uri,payload)
	print r.status_code
	print r.text


def POST():
	name=raw_input("Enter the name u want to insert: ")
	uri= "http://localhost:8081/mainhand"
	payload={"name":name}
	r = requests.post(uri, data=json.dumps(payload))
	
	print r.status_code
	print r.text


def PUT():
	uri="http://localhost:8081/mainhand"
	r = requests.put(uri)
	print r.status_code
	print r.text


def DELETE():
	name=raw_input("Enter the name u want to delete: ")
	uri="http://localhost:8081/mainhand"
	payload={"name":name}
	r = requests.delete(uri, data=json.dumps(payload))
	print r.status_code
	print r.text


selectrequest = {
1:GET,
2:POST,
3:PUT,
4:DELETE}
print selectrequest
selection =-1
while(selection!=5):
	selection=int(input("Enter the type of request\n 1. GET \n 2. POST \n 3. PUT \n 4. DELETE \n 5. QUIT \n"))

 	if (selection >= 0) and (selection <=4):
 		selectrequest[selection]()
