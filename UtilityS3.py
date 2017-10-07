import sys
import os
import time
import boto
import boto.s3
from boto.s3.key import Key

def TestS3():
    AWS_ACCESS_KEY_ID     = os.environ['AWSAccessKeyId']
    AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']

    name_with_datetime = time.strftime("uploads/vis_%Y_%m_%d-%H_%M.png")
    print (name_with_datetime)

    bucket_name = 'natural-interaction'
    conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
                           AWS_SECRET_ACCESS_KEY) 
    location='EU'
    # bucket = conn.create_bucket(bucket_name, location = 'EU')
    bucket = conn.get_bucket(bucket_name, validate=False)

    testfile = "./launch.png"
    print (testfile)
    print (bucket_name)

    def percent_cb(complete, total):
        sys.stdout.write('.')
        sys.stdout.flush()

    k = Key(bucket)
    k.key = name_with_datetime
    k.set_contents_from_filename(testfile,
                                 cb=percent_cb,
                                 num_cb=10)

