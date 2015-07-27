from app import config
from app.db.deploys import Deploy
from app.db.deploys import HostDeploy
from app.db.services import Host
from app.db.services import Service
from app.aws.s3 import latest_filename

from fabric.api import cd
from fabric.api import env
from fabric.api import put
from fabric.api import run
from fabric.api import settings
from fabric.api import sudo

from StringIO import StringIO


class DeployInstance(object):

    """Class the deploys code to a specific. Must be initialized."""

    def __init__(self, host_uuid, service_uuid):
        self.succeeded = True

        self.host = Host.get(uuid=host_uuid)
        self.service = Service.get(uuid=service_uuid)
        self.host_deploy = self.host.get_current_deploy(self.service.uuid)
        self.service_files = self.service.get_files()
        self.f = open('{}/deploys/{}.log'.format(config.LOG_PATH, self.host.instance_id), 'w')

        env.user = self.host.username or 'ec2-user'
        env.forward_agent = True
        env.warn_only = True
        if self.host.public_dns:
            env.host_string = self.host.public_dns
        else:
            env.host_string = self.host.private_ip
        env.key_filename = ['./keys/awsSSH.pem']

    def delete_container(self, tag_name):
        cmd = 'docker ps -a | grep "{}" | cut -f1 -d" "'.format(tag_name)
        output = self._run_command(cmd)
        if len(output) > 0:
            cmd = "docker rm {}".format(tag_name)
            self._run_command(cmd, warn_only=True)

    def delete_images(self):
        cmd = 'docker rmi `sudo docker images -a -q`'
        self._run_command(cmd, warn_only=True)

    def deploy_instance(self, deploying):
        if self.service.is_database:
            return self.deploy_database(deploying)
        else:
            self.deploying = deploying

            self.host_deploy = HostDeploy.get_or_create(deploy_uuid=self.deploying.uuid, host_uuid=self.host.uuid)
            self.f.write('Deploying to {}@{} with key {}.\n'.format(env.user, env.host_string, env.key_filename[0]))

            self._update_instance_files()
            self._pull_new_container()
            self._kill_running_containers()
            self._start_container()

            self.host_deploy = HostDeploy.update(self.host_deploy.uuid, succeeded=self.succeeded)
            return self.succeeded

    def deploy_database(self, deploying):
        self.deploying = deploying

        self.host_deploy = HostDeploy.get_or_create(deploy_uuid=self.deploying.uuid, host_uuid=self.host.uuid)
        self.f.write('Deploying database to {}@{} with key {}.\n'.format(env.user, env.host_string, env.key_filename[0]))

        self._pull_new_container()
        self._kill_container(self.deploying.docker_tag)
        self.delete_container(self.deploying.docker_tag)
        # check for data volumes
        if not self._check_for_data_volume():
            self._create_data_volume()
        self._start_container()
        # restart container?
        self._kill_container(self.deploying.docker_tag)
        self._restart_container()

        self.host_deploy = HostDeploy.update(self.host_deploy.uuid, succeeded=self.succeeded)
        return self.succeeded

    def configure(self):
        # install docker
        sudo('yum update -y', stdout=self.f)
        sudo('yum install -y docker', stdout=self.f)
        sudo('service docker start', stdout=self.f)
        sudo('usermod -a -G docker ec2-user', stdout=self.f)
        # install git
        sudo('yum install -y git', stdout=self.f)
        # add aws configuration information
        run('mkdir -p /home/{}/.aws'.format(env.user))
        with cd('/home/{}/.aws'.format(env.user)):
            file_contents = "[default]\n" \
                            "aws_access_key_id={}\n" \
                            "aws_secret_access_key={}".format(config.AWS_ACCESS_KEY_ID,
                                                              config.AWS_SECRET_ACCESS_KEY)
            self.f.write('cd into /home/{}/.aws\n'.format(env.user))
            result = put(StringIO(file_contents), 'credentials')
            if result.failed:
                self.f.write('failed to put aws credentials on server\n')
        if self.service.is_database:
            # Cron jobs for sudo
            self._run_command('crontab -r', warn_only=True)
            cmd = "crontab -l > file; echo 'SHELL=/bin/bash' >> file; crontab file"
            self._run_command(cmd)
            cmd = 'docker run --rm --volumes-from {}_data -v /home/{}:/backup {} ' \
                  'tar cvf /backup/backup.tar /var/lib/postgresql/data\n'.format(self.service.name.lower(),
                                                                                 env.user,
                                                                                 self.service.docker_image_url)
            self._cron_job(cmd, hour=12, use_sudo=True)

            # Cron job for ec2-user
            self._run_command('crontab -r', warn_only=True, use_sudo=False)
            cmd = "crontab -l > file; echo 'SHELL=/bin/bash' >> file; crontab file"
            self._run_command(cmd, use_sudo=False)
            cmd = 'aws s3 cp /home/{}/backup.tar s3://{}/{}/backups/backup-$(date +"\%Y\%m\%d\%H\%M\%S\%3N").tar' \
                  ' --region "us-west-2"\n'.format(env.user, config.BACKUPS_BUCKET, self.service.name.lower())
            self._cron_job(cmd, hour=12, use_sudo=False)

    def build_container(self):
        pass

    def execute_command(self, tag, command):
        cmd = 'docker exec -it {} {}'.format(tag, command)
        self._run_command(cmd)

    def remove_service(self):
        self.deploying = Deploy.get_latest_deploy(self.service.uuid)
        self.host_deploy = HostDeploy.get_or_create(deploy_uuid=self.deploying.uuid, host_uuid=self.host.uuid)
        self.f.write('Remove service for deploy {}\n'.format(self.deploying.uuid))
        self._kill_running_containers()
        self.delete_container(self.deploying.docker_tag)

    def restart_deploy(self, deploying, hard_restart=False):
        self.deploying = deploying
        self.host_deploy = HostDeploy.get_or_create(deploy_uuid=self.deploying.uuid, host_uuid=self.host.uuid)
        self.f.write('Restarting container for service {} (hard_restart = {}) on'
                     '{}@{} with key {}.\n'.format(self.service.name,
                                                   hard_restart,
                                                   env.user,
                                                   env.host_string,
                                                   env.key_filename[0]))

        self._kill_running_containers()
        if hard_restart:
            self.f.write('Updating deploy files for service {}.\n'.format(self.service.name))
            self._update_instance_files()
            self.delete_container(self.deploying.docker_tag)
            self._start_container()
        else:
            self._restart_container()

        self.host_deploy = HostDeploy.update(self.host_deploy.uuid, succeeded=self.succeeded)
        return self.succeeded

    def _check_for_data_volume(self):
        cmd = 'docker ps -a | grep "{}_data" | cut -f1 -d" "'.format(self.deploying.docker_tag)
        output = self._run_command(cmd)
        if len(output) > 0:
            return True
        return False

    def _create_data_volume(self):
        cmd = 'docker create -v /var/lib/postgresql/data --name {}_data {}' \
              ' /bin/true'.format(self.deploying.docker_tag,
                                  self.service.docker_image_url)
        self._run_command(cmd)

        latest_backup = latest_filename('{}/backups'.format(self.service.name.lower()))
        if latest_backup:
            with cd('/home/{}/.aws'.format(env.user)):
                cmd = "aws s3 cp s3://{}/{}/backups/{} /home/{}/backup.tar" \
                      " --region 'us-west-2'".format(config.BACKUPS_BUCKET,
                                                     self.service.name.lower(),
                                                     latest_backup,
                                                     env.user)
                self._run_command(cmd, use_sudo=False)

            cmd = 'docker run --rm --volumes-from {}_data -v /home/{}:/backup {}' \
                  ' tar -xvf /backup/backup.tar'.format(self.deploying.docker_tag,
                                                        env.user,
                                                        self.service.docker_image_url)
            self._run_command(cmd)
            cmd = 'rm /home/{}/backup.tar'.format(env.user)
            self._run_command(cmd, warn_only=True, use_sudo=False)

    def _cron_job(self, cron_cmd, min=None, hour=None, use_sudo=False):
        min = "/{}".format(min) if min else ""
        hour = "/{}".format(hour) if hour else ""
        cmd = "crontab -l > file; echo '*{} *{} * * * {}' >> file; crontab file".format(min, hour, cron_cmd)
        self._run_command(cmd, use_sudo=use_sudo)

    def _kill_container(self, container_name):
        cmd = 'docker ps | grep "{}" | cut -f1 -d" "'.format(container_name)
        output = self._run_command(cmd)
        if len(output) > 0:
            cmd = 'docker kill {}'.format(container_name)
            self._run_command(cmd, warn_only=True)

    def _kill_running_containers(self):
        cmd = 'docker ps | grep "{}.*" | cut -f1 -d" "'.format(self.service.name.lower())
        output = self._run_command(cmd)
        if len(output) > 0:
            cmd = 'docker kill $(sudo docker ps | grep "{}-.*" | cut -f1 -d" ")'.format(self.service.name.lower())
            self._run_command(cmd, warn_only=True)

    def _pull_new_container(self):
        cmd = "docker login -e '{}' -p '{}' -u '{}'".format(config.DOCKER_EMAIL,
                                                            config.DOCKER_PASSWORD,
                                                            config.DOCKER_USERNAME)
        self._run_command(cmd)
        cmd = "docker pull {}".format(self.service.docker_image_url)
        self._run_command(cmd)

    def _restart_container(self):
        cmd = "docker restart {}".format(self.deploying.docker_tag)
        self._run_command(cmd)

    def _start_container(self):
        extra_commands = ""
        for env_name, env_value in self.service.get_attributes_dict(attr_type='environment').iteritems():
            extra_commands = extra_commands + "-e {}={} ".format(env_name, env_value)
        for env_name, env_value in self.service.get_attributes_dict(attr_type='database_auth').iteritems():
            extra_commands = extra_commands + "-e {}={} ".format(env_name, env_value)
        if self.service.is_database:
            files = '--volumes-from {}_data'.format(self.deploying.docker_tag)
        else:
            files = "-v /home/{}/keys:/opt/code/keys".format(env.user)
        cmd = "docker run -p {}:{} {} {} -d --name {} {}".format(self.service.external_port,
                                                                 self.service.internal_port,
                                                                 files,
                                                                 extra_commands.rstrip(),
                                                                 self.deploying.docker_tag,
                                                                 self.service.docker_image_url)
        self._run_command(cmd)

    def _update_instance_files(self):
        # Create server files and put on server in home directory
        self.f.write('Updating instance files.\n')
        for service_file in self.service_files:
            run('mkdir -p /home/{}/keys'.format(env.user))
            with cd('/home/{}/keys'.format(env.user)):
                self.f.write('cd into /home/{}/keys\n'.format(env.user))
                self.f.write('put file {} on server\n'.format(service_file.name))
                if service_file.mode:
                    result = put(StringIO(service_file.body),
                                 '{}'.format(service_file.name),
                                 mode=int(service_file.mode),
                                 use_sudo=True)
                else:
                    result = put(StringIO(service_file.body), '{}'.format(service_file.name))
                if result.failed:
                    self.f.write('failed to put file {} on server\n'.format(service_file.name))
                    self.succeeded = False
                    return

    def _run_command(self, cmd, warn_only=False, use_sudo=True):
        self.f.write('{}\n'.format(cmd))
        with settings(warn_only=warn_only):
            if use_sudo:
                output = sudo(cmd, stdout=self.f)
            else:
                output = run(cmd, stdout=self.f)
            if output.failed:
                self.succeeded = False
                if warn_only is False:
                    self.host_deploy = HostDeploy.update(self.host_deploy.uuid, succeeded=self.succeeded)
                    raise Exception("Deploying failed on command {}".format(cmd))
        return output.stdout
