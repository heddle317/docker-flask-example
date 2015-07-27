import time

from app import queue
from app import config
from app.aws import connect_ec2
from app.aws import connect_ec2_elb
from app.aws.deploy_instance import DeployInstance
from app.db.services import Service
from app.db.services import Host


def activate_instance(host, service):
    conn = connect_ec2_elb()
    lbs = conn.get_all_load_balancers(load_balancer_names=[service.get_loadbalancer().name])
    if len(lbs) > 0:
        lb = lbs[0]
        lb.register_instances([host.instance_id])
        return host.activate(service, active=True)
    return host


def create_instance(service_uuid, instance_type, user_name, image_id):
    service = Service.get(uuid=service_uuid)
    subnet_id = config.PRIVATE_SUBNET_ID
    if 'deploy' in service.name.lower():
        subnet_id = config.PUBLIC_SUBNET_ID

    conn = connect_ec2()
    reservation = conn.run_instances(image_id,
                                     key_name=service.key_name,
                                     instance_type=instance_type,
                                     security_group_ids=config.INSTANCE_SG,
                                     subnet_id=subnet_id)
    instances = reservation.instances
    instance = instances[0]
    host = Host.create_or_update(instance.id,
                                 private_ip=instance.private_ip_address,
                                 public_ip=instance.ip_address,
                                 public_dns=instance.public_dns_name,
                                 image_type=instance_type,
                                 image_id=image_id,
                                 username=user_name)
    host.add_service(service.uuid)
    instance.add_tag("Name", "{}-{}".format(service.name.lower(), host.uuid))
    queue().enqueue_call(func=check_instance_for_configuration, args=[host.uuid, service_uuid], timeout=120)
    return host


def update_instances_from_ids(service_uuid, instance_ids, configure=True):
    service = Service.get(uuid=service_uuid)

    conn = connect_ec2()
    reservation = conn.get_all_instances(instance_ids=instance_ids)
    for r in reservation:
        for instance in r.instances:
            host = Host.create_or_update(instance.id,
                                         private_ip=instance.private_ip_address,
                                         public_ip=instance.ip_address,
                                         public_dns=instance.public_dns_name)
            host.add_service(service.uuid)
            instance.add_tag("Name", "{}-{}".format(service.name.lower(), host.uuid))
            queue().enqueue_call(func=check_instance_for_configuration, args=[host.uuid, service.uuid], timeout=120)


def check_instance_for_configuration(host_uuid, service_uuid):
    conn = connect_ec2()
    host = Host.get(uuid=host_uuid)
    reservations = conn.get_all_instances(instance_ids=[host.instance_id])
    if len(reservations) == 0 or len(reservations[0].instances) == 0:
        raise Exception('There are no AWS instances for this host.')
    instance = reservations[0].instances[0]
    if instance.state == 'running':
        queue().enqueue_call(func=configure_instance, args=[host_uuid, service_uuid])
        return
    time.sleep(5)
    queue().enqueue_call(func=check_instance_for_configuration, args=[host_uuid, service_uuid], timeout=120)


def configure_instance(host_uuid, service_uuid):
    dp = DeployInstance(host_uuid, service_uuid)
    dp.configure()


def remove_service(host_uuid, service_uuid):
    dp = DeployInstance(host_uuid, service_uuid)
    dp.remove_service()


def deactivate_instance(host, service):
    conn = connect_ec2_elb()
    lbs = conn.get_all_load_balancers(load_balancer_names=[service.get_loadbalancer().name])
    if len(lbs) > 0:
        lb = lbs[0]
        lb.deregister_instances([host.instance_id])
        return host.activate(service, active=False)
    return host


def remove_service_from_host(host, service):
    host.remove_service(service.uuid)
    if host.is_empty():
        terminate_instance(host.uuid)
    else:
        queue().enqueue_call(func=remove_service, args=[host.uuid, service.uuid], timeout=90)


def terminate_instance(host_uuid):
    host = Host.get(uuid=host_uuid)

    conn = connect_ec2()
    terminated_instances = conn.terminate_instances(instance_ids=[host.instance_id])
    addresses = conn.get_all_addresses(filters={'private_ip_address': [host.private_ip]})
    for address in addresses:
        address.disassociate()
        address.release()
    for instance in terminated_instances:
        Host.soft_delete(instance_id=instance.id)
