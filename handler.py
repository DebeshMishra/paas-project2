from boto3 import client as boto3_client
import face_recognition
import pickle
import sys
import json

input_bucket = "cse546-2-input"
output_bucket = "cse546-2-output"

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):

	print("Received event: " + json.dumps(event['Records'][0]['s3']['object']['key']))
	return 'Hello from AWS Lambda using Python' + sys.version + '!'