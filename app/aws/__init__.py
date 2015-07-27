from app import config

from boto.ec2 import connect_to_region
from boto.ec2 import get_region
from boto.ec2.elb import connect_to_region as connect_elb
from boto.iam.connection import IAMConnection
from boto.vpc import VPCConnection


def connect_ec2():
    region = "us-west-2"
    conn = connect_to_region(region,
                             aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)
    return conn


def connect_ec2_elb():
    region = "us-west-2"
    conn = connect_elb(region,
                       aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)
    return conn


def connect_ec2_vpc():
    region = get_region("us-west-2")
    conn = VPCConnection(aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                         region=region)
    return conn


def connect_ec2_iam():
    conn = IAMConnection(aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY)
    return conn
