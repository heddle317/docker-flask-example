from app import config

from boto.s3.connection import S3Connection
# from boto.s3.key import Key


def latest_filename(path):
    conn = S3Connection(config.AWS_ACCESS_KEY_ID, config.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(config.BACKUPS_BUCKET)
    # key = Key(bucket)

    l = [(k.last_modified, k.name) for k in bucket.list(path)]
    if len(l) == 0:
        return None
    l.sort(key=lambda x: x[0], reverse=True)
    return l[0][1].split('/')[2]
