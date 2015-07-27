from app import queue
from app.aws.deploy_service import DeployService
from app.db.services import Deploy


def delete_container(service, deploy_uuid):
    dp = DeployService(service.uuid, deploy_uuid=deploy_uuid)
    return dp.delete_container()


def deploy_database_service(service, user_uuid):
    deploy = Deploy.create_deploy(service,
                                  user_uuid=user_uuid)
    queue().enqueue_call(func=deploy_f, args=[service.uuid, deploy.uuid])
    return deploy


def deploy_service(service, user_uuid):
    build_uuid = service.get_latest_build().uuid if service.get_latest_build() else None
    deploy = Deploy.create_deploy(service,
                                  user_uuid=user_uuid,
                                  build_uuid=build_uuid)
    queue().enqueue_call(func=deploy_f, args=[service.uuid, deploy.uuid], timeout=300)
    return deploy


def restart_deploy(service, user_uuid, deploy, hard_restart=False):
    queue().enqueue_call(func=restart_f, args=[service.uuid, deploy.uuid], kwargs={'hard_restart': hard_restart})
    return deploy


def run_script(service, script_name, args):
    dp = DeployService(service.uuid, None)
    dp.run_script(script_name, args=args)


def deploy_f(service_uuid, deploy_uuid):
    dp = DeployService(service_uuid, deploy_uuid)
    dp.deploy()
    dp.delete_images()


def restart_f(service_uuid, deploy_uuid, hard_restart=False):
    dp = DeployService(service_uuid, deploy_uuid)
    dp.restart_deploy(hard_restart=hard_restart)
