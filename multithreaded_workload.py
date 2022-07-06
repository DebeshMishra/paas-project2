from boto3 import client as boto3_client
import os
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

input_bucket = "cse546-project2-paas-input"
output_bucket = "cse546-project2-paas-output"
test_cases = "test_cases/"

def clear_input_bucket():
	global input_bucket
	s3 = boto3_client('s3')
	list_obj = s3.list_objects_v2(Bucket=input_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=input_bucket, Key=key)
	except:
		print("Nothing to clear in input bucket")
	
def clear_output_bucket():
	global output_bucket
	s3 = boto3_client('s3')
	list_obj = s3.list_objects_v2(Bucket=output_bucket)
	try:
		for item in list_obj["Contents"]:
			key = item["Key"]
			s3.delete_object(Bucket=output_bucket, Key=key)
	except:
		print("Nothing to clear in output bucket")

def upload_to_input_bucket_s3(path, name):
	global input_bucket
	s3 = boto3_client('s3')
	s3.upload_file(path + name, input_bucket, name)
	print(f"Uploaded to input bucket..  name: {str(name)}")

	
def upload_files(test_case):	
	global input_bucket
	global output_bucket
	global test_cases
	
	
	# Directory of test case
	test_dir = test_cases + test_case + "/"

	filenames = []

	# Iterate over each video
	# Upload to S3 input bucket
	for filename in os.listdir(test_dir):
		if filename.endswith(".mp4") or filename.endswith(".MP4"):
			filenames.append(filename)

	# upload_to_input_bucket_s3(test_dir, filename)
	with ThreadPoolExecutor(max_workers=100) as executor:
		executor.map(lambda file : upload_to_input_bucket_s3(test_dir, file), filenames)

def workload_generator():
	
	# print("Running Test Case 0")
	# upload_files("test_case_0")

	print("Running Test Case 2")
	upload_files("test_case_2")
	

clear_input_bucket()
clear_output_bucket()	
workload_generator()	

	

