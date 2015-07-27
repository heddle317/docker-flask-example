import os

ENV = os.environ.get('ENVIRONMENT', 'dev')

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
ROOT_PATH = BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

REDIS_URL = 'redis://localhost:6379'

STATIC_FOLDER = os.path.join(ROOT_PATH, 'static')
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, 'templates')
SECRET_KEY = os.environ.get('SECRET_KEY')
CSRF_ENABLED = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(ROOT_PATH, 'db_repository')
MODEL_HASH = os.environ.get('MODEL_HASH')
BUGSNAG_KEY = os.environ.get('BUGSNAG_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
POSTMARKAPP_API_KEY = os.environ.get('POSTMARKAPP_API_KEY')
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
S3_BASE = 'https://s3-us-west-2.amazonaws.com'

IMAGE_BUCKET = os.environ.get('IMAGE_BUCKET')
STATIC_BUCKET = os.environ.get('STATIC_BUCKET')
IMAGES_BASE = '{}/{}'.format(S3_BASE, IMAGE_BUCKET)
STATIC_BASE = '()/{}'.format(S3_BASE, STATIC_BUCKET)
BACKUPS_BUCKET = 'backups.makemeup.co'

LOGENTRIES_TOKEN = os.environ.get('LOGENTRIES_TOKEN')

DOCKER_EMAIL = os.environ.get('DOCKER_EMAIL')
DOCKER_PASSWORD = os.environ.get('DOCKER_PASSWORD')
DOCKER_USERNAME = os.environ.get('DOCKER_USERNAME')

GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')

TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_SECRET = os.environ.get('TWILIO_SECRET')
TWILIO_FROM = os.environ.get('TWILIO_FROM')

ACCOUNTS_URL = os.environ.get('ACCOUNTS_SERVICE_URL')

PUBLIC_SUBNET_ID = os.environ.get('PUBLIC_SUBNET_ID')
PRIVATE_SUBNET_ID = os.environ.get('PRIVATE_SUBNET_ID')
VPC_ID = os.environ.get('VPC_ID')
PRIVATE_LB_SG = os.environ.get('PRIVATE_LB_SG', '').split(',')
PUBLIC_LB_SG = PRIVATE_LB_SG + os.environ.get('PUBLIC_LB_SG', '').split(',')
INSTANCE_SG = os.environ.get('INSTANCE_SG', '').split(',')
CERTIFICATE_ID = os.environ.get('CERTIFICATE_ID')
SENTRY_DSN = os.environ.get('SENTRY_DSN')
ASYNC_SENTRY_DSN = os.environ.get('ASYNC_SENTRY_DSN')
SQLALCHEMY_POOL_RECYCLE = 3600

if ENV == 'dev':
    PORT = 7000
    APP_BASE_LINK = 'http://localhost:' + str(PORT)
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/deploy_db'
    LOG_PATH = os.path.join(ROOT_PATH, 'logs')
else:
    LOG_PATH = '/var/log'
    APP_BASE_LINK = 'https://deploy.makemeup.co'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(os.environ.get('POSTGRES_ENV_POSTGRES_USER'),
                                                                   os.environ.get('POSTGRES_ENV_POSTGRES_PASSWORD'),
                                                                   os.environ.get('POSTGRES_PORT_5432_TCP_ADDR'),
                                                                   os.environ.get('POSTGRES_PORT_5432_TCP_PORT'),
                                                                   os.environ.get('POSTGRES_ENV_POSTGRESQL_DB'))
