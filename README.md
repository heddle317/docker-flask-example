# docker-flask-example
A generic python/Flask app with a Docker file

# Getting started with Docker
1. Install DockerToolbox (https://www.docker.com/toolbox)
2. Install VirtualBox (https://www.virtualbox.org/wiki/Downloads)
3. Open the newly installed "Docker" folder (in Applications for Mac)
4. Click "Docker Quickstart Terminal"
5. Run: docker pull heddle317/docker-flask-example
6. Run: docker run -p 8080:80 -e ENVIRONMENT='production' -d --name=flask_app heddle317/docker-flask-example
7. Run: VBoxManage controlvm default natpf1 "flask_app,tcp,127.0.0.1,8080,,8080"
8. Go to localhost:8080 in your browser and you should see "Hello, world!"

# Creating your own version of this repo
1. Fork this repository.
2. Create an account at Dockerhub.com
3. Click the "Create" dropdown in the far top right corner (not the "Create Repository+" button)
4. Select "Create Automated Build"
5. Link your Github (or Bitbucket) account, select your user, select the github repo, etc.
6. Click the "Trigger a build" button, go to the "Build Details" tab and you should see a new build for your container.

# Testing your docker container when there are changes
1. Clone your new repository down to your laptop
2. Make a change to your Flask application (white space changes or comments are easy to test).
3. Push your change to github.
4. Go to your dockerhub account, click on your automated build repository, and click the build details tab.
5. Once the build is finished, go to boot2docker.
6. Run: docker pull [dockerHubUsername]/docker-flask-example (if you changed the name of the repo, reflect that here)
7. Run: docker run -p 8080:80 -e ENVIRONMENT='production' -d --name=flask_app [dockerHubUsername]/[repoName]
8. Go to localhost:8080 in your browser and you should see your application.

# Running your docker image in AWS
1. Make an AWS account (if you don't have one).
2. Create your own VPC (OPTIONAL: if you don't have one or want a new one).
3. Create a new public subnet.
4. Create an instance in your new public subnet.
5. Ssh to your new machine: ssh -i aws.pem ec2-user@[instance-public-dns]
6. Run: sudo yum update -y
7. Run: sudo yum install -y docker
8. Run: sudo service docker start
9. Run (only necessary for private docker images): sudo docker login -e '[email]' -p '[password]' -u '[dockerHubUsername]'
10. Run: sudo docker pull [dockerHubUsername]/[repoName]
11. Run: sudo docker run -p 80:80 -e ENVIRONMENT='production' -d --name=flask_app [dockerHubUsername]/[repoName]
12. Go to [instance-public-dns] to see your web app.

# Setting up your python development environment (OPTIONAL)
1. If your laptop is not setup for python, follow these instructions (http://newcoder.io/pyladiessf/)
2. Create a new virtualenv with venv or mkvirtualenv
3. Run: pip install -r ./files/requirements.txt
4. Create a keys.sh file with your sensitive information (e.g. export ENVIRONMENT='dev' and SECRET_KEY='')
5. Run: ./run.sh web.py
6. You should be able to see your application running on localhost:7010 (that port is configured in the app/config.py file)
