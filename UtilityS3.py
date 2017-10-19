import sys
import os
import time
import boto
import boto.s3
from boto.s3.key import Key

def UploadFileToS3(filename):
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    bucket_name = 'natural-interaction'

    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY) 
    
        location='EU'
        # bucket = conn.create_bucket(bucket_name, location = 'EU')
        bucket = conn.get_bucket(bucket_name, validate=False)

        print(filename)
        print(bucket_name)

        def percent_cb(complete, total):
            sys.stdout.write('.')
            sys.stdout.flush()

        k = Key(bucket)
        k.key = filename
        k.set_contents_from_filename(filename,
                                     cb=percent_cb,
                                     num_cb=10)
    except:
        print ("upload to S3 error")
        print (sys.exc_info())
        return False

    return True

def ListFilesInCacheOnS3():
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    bucket_name = 'natural-interaction'

    try:
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                               AWS_SECRET_ACCESS_KEY) 
    
        location='EU'
        bucket = conn.get_bucket(bucket_name, validate=False)

        print(bucket_name)

        files = bucket.list(prefix='cache')  # cache/
        
        for key in files: 
            print(key.key)
        
    except:
        print ("list cache on S3 error")
        print (sys.exc_info())
        return False

    return True

