import boto3
import face_recognition
import pickle
from botocore.exceptions import ClientError
import os

output_bucket = "cse546-project2-paas-output"
dynamodb_table_name = 'paas-2-student'

access_key = 'AKIAR2FYKC34HDRIALXK'
secret_key = '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'
region = 'us-east-1'
s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
dynamodb = boto3.resource('dynamodb', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)

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

	# Path to store video locally
	path = '/tmp/'
	video_file_path = str(path) + key

	frames_path = f'{path}frames/'
	if not os.path.exists(frames_path):
		os.mkdir(frames_path)

	print(f"Downloading file {key}")
	# Downloading the video file from S3 and storing in local
	try:
		s3.download_file(bucket, key, video_file_path)
	except ClientError as e:
		if e.response['Error']['Code'] == '404':
			print(f'The video file does not exist in s3://{bucket}/{key}')
			return
		else: raise e

	# Extracting frames using ffmpeg
	os.system("ffmpeg -i " + str(video_file_path) + " -r 1 " + str(frames_path) + "image-%3d.jpeg")

	# Loop through frames and find first face match
	frames = sorted(os.listdir(frames_path))
	print(frames)
	for frame in frames:
		img = face_recognition.load_image_file(os.path.join(frames_path, frame))
		face_encodings = face_recognition.face_encodings(img)
		if len(face_encodings) > 0:
			img_enc = face_encodings[0]
			break

	# Read the encoding file
	encoding_file = '/home/app/encoding'
	face_encoding = open_encoding(encoding_file)

	# Getting the corresponding match from encoding file
	result_arr = face_recognition.compare_faces(face_encoding['encoding'], img_enc)
	idx = result_arr.index(True)
	name = list(face_encoding['name'])[idx]
	print(name)

	student_table = dynamodb.Table(dynamodb_table_name)
	item = student_table.get_item(Key={'name': name})['Item']
	print(item)
	csv = f"{item['name']},{item['major']},{item['year']}"
	print(csv)

	s3.put_object(Bucket=output_bucket, Key=key.replace(".mp4", ".csv"), Body=csv)
	return csv