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

# Add logging conf file
RUN wget -O ./remote_syslog.tar.gz https://github.com/papertrail/remote_syslog2/releases/download/v0.14/remote_syslog_linux_amd64.tar.gz && tar xzf ./remote_syslog.tar.gz && cp ./remote_syslog/remote_syslog /usr/bin/remote_syslog && rm ./remote_syslog.tar.gz && rm -rf ./remote_syslog/
ADD ./files/log_files.yml /etc/log_files.yml

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
