from boto3 import client as boto3_client
import face_recognition
import pickle
import sys
from botocore.exceptions import ClientError
import os

output_bucket = "cse546-project2-paas-output"

access_key = 'AKIAR2FYKC34HDRIALXK'
secret_key = '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'
region = 'us-east-1'
s3 = boto3_client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):
	
	# Getting the Bucket and Key name from S3 client
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = event['Records'][0]['s3']['object']['key']

	# Fetching the video file from S3
	try:
		video = s3.get_object(Bucket=bucket, Key=key)
	except Exception as e:
		print(e)
		print(
            'Error occurred while retrieving the video {} from the bucket {}.'.format(
                key,
                bucket))
		raise e
	
    # Path to store video locally
	path = '/tmp/'
	video_file_path = str(path) + key

	# Downloading the video file from S3 and storing in local
	try:
		s3.download_file(bucket, key, video_file_path)
	except ClientError as e:
		if e.response['Error']['Code'] == '404':
			print('The video file does not exist in s3://{}/{}'.format(bucket, key))
		else: raise e
	
	# Extracting frames using ffmpeg
	os.system("ffmpeg -i " + str(video_file_path) + " -r 1 " + str(path) + "image-%3d.jpeg")

	# Reading first image file and its encoding
	img = face_recognition.load_image_file(path+'image-001.jpeg')
	img_enc = face_recognition.face_encodings(img)[0]

	# Read the encoding file
	encoding_file = '/home/app/encoding'
	face_encoding = open_encoding(encoding_file)

	# Getting the corresponding match from encoding file
	resultArr = face_recognition.compare_faces(face_encoding['encoding'], img_enc)
	idx = resultArr.index(True)
	res = list(face_encoding['name'])[idx]
	print(res)

	#print("Received event: " + json.dumps(event['Records'][0]['s3']['object']['key']))
	return 'Hello from AWS Lambda using Python' + sys.version + '!'