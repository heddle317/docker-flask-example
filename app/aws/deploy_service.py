from app import queue
from app.apis.github_apis import text_github_users_diff
from app.aws.deploy_instance import DeployInstance
from app.db.deploys import Deploy
from app.db.services import Build
from app.db.services import Service
from app.db.user import User
from app.utils.datetime_tools import now_utc


class DeployService(object):

    def __init__(self, service_uuid, deploy_uuid):
        self.service = Service.get(uuid=service_uuid)
        if not deploy_uuid:
            self.deploying = None
        else:
            self.deploying = Deploy.get(uuid=deploy_uuid)
        self.deploy_succeeded = True
        self.current_deploy = self.service.get_current_deploy()

    def delete_container(self):
        for host in self.service.get_hosts():
            dp = DeployInstance(host.uuid, self.service.uuid)
            dp.delete_container(self.deploying.docker_tag)
        deploy = Deploy.update(self.deploying.uuid, currently_running=False, on_machine=False)
        return deploy

    def delete_images(self):
        for host in self.service.get_hosts():
            dp = DeployInstance(host.uuid, self.service.uuid)
            dp.delete_images()

    def deploy(self):
        self.deploying = Deploy.update(self.deploying.uuid, last_deployed=now_utc(), started=True)
        for host in self.service.get_hosts():
            dp = DeployInstance(host.uuid, self.service.uuid)
            succeeded = dp.deploy_instance(self.deploying)
            self.deploy_succeeded = self.deploy_succeeded & succeeded
        self.deploying = Deploy.update(self.deploying.uuid,
                                       currently_running=self.deploy_succeeded,
                                       on_machine=self.deploy_succeeded,
                                       succeeded=self.deploy_succeeded,
                                       finished=True)
        if self.current_deploy and self.deploying.uuid != self.current_deploy.uuid:
            self.current_deploy = Deploy.update(self.current_deploy.uuid, currently_running=not self.deploy_succeeded)
        if self.deploy_succeeded and self.service.has_database:
            self.run_script('run_migrations.py')
        self._text_admins()

    def restart_deploy(self, hard_restart=False):
        self.deploying = Deploy.update(self.deploying.uuid, last_deployed=now_utc())
        for host in self.service.get_hosts():
            dp = DeployInstance(host.uuid, self.service.uuid)
            succeeded = dp.restart_deploy(self.deploying, hard_restart=hard_restart)
            self.deploy_succeeded = self.deploy_succeeded & succeeded

        if self.deploy_succeeded:
            current_deploy = self.service.get_current_deploy()
            if self.deploying == current_deploy:
                return
            Deploy.update(uuid=current_deploy.uuid, currently_running=False)
            Deploy.update(uuid=self.deploying.uuid, currently_running=True)
        self._text_admins()

    def run_script(self, script_name, args=None):
        hosts = self.service.get_hosts()
        if len(hosts) > 0:
            # only need to run this on one host
            host = hosts[0]
            current_deploy = self.service.get_current_deploy()
            dp = DeployInstance(host.uuid, self.service.uuid)
            command = './run.sh ./scripts/{}'.format(script_name)
            if args:
                for arg in args:
                    command = command + ' \'{}\''.format(arg)
            dp.execute_command(current_deploy.docker_tag, command)

    def _text_admins(self):
        m = 'SUCCEEDED' if self.deploy_succeeded else 'FAILED'
        message = "DEPLOY {}: {}.".format(m, self.service.name)
        if not self.current_deploy or not self.deploying.build_uuid:
            queue().enqueue_call(func=User.text_users, args=[None, message])
            return
        current_build = Build.get(uuid=self.current_deploy.build_uuid)
        latest_build = Build.get(uuid=self.deploying.build_uuid)
        queue().enqueue_call(func=text_github_users_diff,
                             args=(self.service.uuid, current_build.uuid, latest_build.uuid, message))
