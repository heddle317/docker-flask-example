from app import config
from app.aws import connect_ec2_elb
from app.db.services import LoadBalancer
from app.db.services import Service

from boto.ec2.elb import HealthCheck


def create_service_elb(service, name):
    conn = connect_ec2_elb()
    lb = None
    try:
        lbs = conn.get_all_load_balancers(load_balancer_names=[name])
        if len(lbs) > 0:
            lb = lbs[0]
    except:
        pass
    if lb is None:
        ports = [(80, service.external_port, 'http')]
        if not service.internal:
            ports.append((443, service.external_port, 'https', config.CERTIFICATE_ID))
        if service.internal:
            scheme = 'internal'
            subnets = [config.PRIVATE_SUBNET_ID]
            security_group_ids = config.PRIVATE_LB_SG
        else:
            scheme = 'internet-facing'
            subnets = [config.PUBLIC_SUBNET_ID]
            security_group_ids = config.PUBLIC_LB_SG
        lb = conn.create_load_balancer(name,
                                       [],
                                       listeners=ports,
                                       scheme=scheme,
                                       security_groups=security_group_ids,
                                       subnets=subnets)
    hc = HealthCheck(
        interval=60,
        healthy_threshold=3,
        unhealthy_threshold=5,
        target='HTTP:{}/index.html'.format(service.external_port)
    )
    lb.configure_health_check(hc)

    lb = LoadBalancer.create(service_uuid=service.uuid, elb_dns_name=lb.dns_name, name=name)


def update_service_elb(service):
    conn = connect_ec2_elb()
    service_lb = service.get_loadbalancer()
    lbs = conn.get_all_load_balancers(load_balancer_names=[service_lb.name])
    if len(lbs) > 0:
        lb = lbs[0]
        LoadBalancer.update(service_lb.uuid, elb_dns_name=lb.dns_name)


def delete_service_elb(service):
    conn = connect_ec2_elb()
    lbs = conn.get_all_load_balancers(load_balancer_names=[service.get_loadbalancer().name])
    if len(lbs) > 0:
        lb = lbs[0]
        lb.delete()
    LoadBalancer.delete(service.get_loadbalancer().uuid)
    return service


def update_service_elb_visibility(service, internal):
    if internal == service.internal:
        return service
    # TO DO: Figure out how to update an elb's scheme
    # conn = connect_ec2_elb()
    # scheme = 'internal' if service.internal else 'internet-facing'
    modified = False
    if modified:
        service = Service.update(service.uuid, internal=internal)
    return service
