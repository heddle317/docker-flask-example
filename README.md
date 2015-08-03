# docker-flask-example
A generic python/Flask app with a Docker file

# Getting started with this repository locally
1. Install Boot2Docker https://docs.docker.com/mac/started/
2. Launch boot2docker
3. Run: docker pull heddle317/docker-flask-example
4. Run: docker run -p 8080:80 -e ENVIRONMENT='production' -d --name=flask_app heddle317/docker-flask-example
5. Run: VBoxManage controlvm boot2docker-vm natpf1 "flask_app,tcp,127.0.0.1,8080,,8080"
6. Go to localhost:8080 in your browser and you should see "Hello, world!"

# Creating your own version
1. Fork this repository.
2. Create an account at Dockerhub.com
3. Create a new repository (automated build) in dockerhub
4. Select build from Github
5. Fill out relevant information

# Setting up your development environment
1. Clone your new repository down to your laptop
2. If your laptop is not setup for python, follow these instructions (http://newcoder.io/pyladiessf/)
3. Create a new virtualenv with venv or mkvirtualenv
4. Run: pip install -r ./files/requirements.txt
5. Run: ./run.sh web.py
6. You should be able to see your application running on localhost:7000 (that port is configured in the app/config.py file)

# Testing your docker container
1. Make a change to your Flask application and verify it works locally.
2. Push your change to github.
3. Go to your dockerhub account, click on your automated build repository, and click the build details tab.
4. Once the build is finished, go to boot2docker.
5. Run: docker pull [dockerHubUsername]/docker-flask-example (if you changed the name of the repo, reflect that here)
6. Run: docker run -p 8080:80 -e ENVIRONMENT='production' -d --name=flask_app [dockerHubUsername]/[repoName]
7. Run: VBoxManage controlvm boot2docker-vm natpf1 "flask_app,tcp,127.0.0.1,8080,,8080"
8. Go to localhost:8080 in your browser and you should see your application.

# Running your docker image in AWS
1. Make an AWS account (if you don't have one).
2. Create your own VPC (if you don't have one or want a new one).
3. Create a new public subnet.
4. Create an instance in your new public subnet. (Amazon Linux ami-e7527ed7)
5. Ssh to your new machine: ssh -i aws.pem ec2-user@[instance-public-dns]
6. Run: yum update -y
7. Run: yum install -y docker
8. Run: service docker start
9. Run: usermod -a -G docker ec2-user
10. Run (only necessary for private docker images): docker login -e '[email]' -p '[password]' -u '[dockerHubUsername]'
11. Run: docker pull [dockerHubUsername]/[repoName]
12. Run: docker run -p 8080:80 -e ENVIRONMENT='production' -d --name=flask_app [dockerHubUsername]/[repoName]
11. Go to [instance-public-dns] to see your web app.
