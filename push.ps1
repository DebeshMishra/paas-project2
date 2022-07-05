docker build -f Dockerfile -t cse546-project2 .
docker tag cse546-project2:latest 437562426674.dkr.ecr.us-east-1.amazonaws.com/cse546-project2:latest
docker push 437562426674.dkr.ecr.us-east-1.amazonaws.com/cse546-project2:latest
