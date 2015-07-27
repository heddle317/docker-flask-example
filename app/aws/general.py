from app.aws import connect_ec2
from app.aws import connect_ec2_vpc


def get_all_security_groups():
    conn = connect_ec2()
    sg = conn.get_all_security_groups()
    return_values = []
    for s in sg:
        return_values.append(
            {'name': s.name,
             'label': s.name,
             'id': s.id,
             'value': s.id,
             'vpc_id': s.vpc_id})
    return return_values


def get_all_keypairs():
    conn = connect_ec2()
    keys = conn.get_all_key_pairs()
    keys = [{'label': key.name, 'value': key.name} for key in keys]
    return keys


def get_all_subnets():
    conn = connect_ec2_vpc()
    subnets = conn.get_all_subnets()
    values = []
    for s in subnets:
        values.append({'label': s.id,
                       'id': s.id,
                       'value': s.id,
                       'vpc_id': s.vpc_id})
    return values


def get_all_vpcs():
    conn = connect_ec2_vpc()
    vpcs = conn.get_all_vpcs()
    vpcs = [{'label': vpc.id, 'value': vpc.id} for vpc in vpcs]
    return vpcs
