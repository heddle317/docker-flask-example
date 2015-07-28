FROM ubuntu:14.04
MAINTAINER Kate Heddleston <kate@makemeup.co>

RUN DEBIAN_FRONTEND=noninteractive apt-get update --fix-missing && apt-get install -y build-essential git python python-dev python-setuptools nginx supervisor bcrypt libssl-dev libffi-dev libpq-dev vim redis-server rsyslog wget
RUN easy_install pip

# stop supervisor service as we'll run it manually
RUN service supervisor stop
RUN mkdir /var/log/gunicorn
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default

WORKDIR /code/

# Add service.conf
ADD ./files/service.conf /code/
RUN ln -s /code/service.conf /etc/nginx/sites-enabled/

# Add supervisor
ADD ./files/supervisord.conf /code/
RUN ln -s /code/supervisord.conf /etc/supervisor/conf.d/

# Add requirements and install
ADD ./files/requirements.txt /code/
RUN pip install -r ./requirements.txt

# Add github repo code to code file
ADD . /code/
RUN mkdir /code/logs

# expose port(s)
EXPOSE 80

CMD ./run_service.sh
