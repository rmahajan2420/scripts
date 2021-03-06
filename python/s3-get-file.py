#!/usr/bin/python

import boto
import argparse, sys, logging

def get_creds():

    # By default empty, boto will look for environment variables
    # AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    ACCESSKEY=''
    SECRETKEY=''

    return ACCESSKEY, SECRETKEY

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", dest="url", required=True,
                                            help="the s3 url, e.g s3://bucketname/path/to/file")
    parser.add_argument("-f", "--file", dest="filename", required=True,
                                            help="the local filename to write, e.g. ~/Users/butlern/my-file.txt")
    parser.add_argument("-l", "--log", dest="loglevel", default='CRITICAL',
                                            choices=['CRITICAL','FATAL','ERROR','WARN','WARNING','INFO','DEBUG','NOTSET'],
                                            help="the loglevel sets the amount of output you want")    
    return parser.parse_args()

def get_numeric_loglevel(loglevel):
    return getattr(logging, loglevel.upper())

def get_conn(accesskey, secretkey):
    if accesskey and secretkey:
        return boto.connect_s3(accesskey,secretkey)
    else:
        return boto.connect_s3()

def parse_url(url):
    if url.startswith('s3://'):
        u = url.lstrip('s3://').split('/')
        if len(u) > 1:
            u.reverse()
            bucket = u.pop()
            u.reverse()
            path = "/".join(u)
            return bucket, path
        else:
            logging.error("Invalid URL: %s" % url)
            sys.exit(1)
    else:
        logging.error("Invalid URL: %s" % url)
        sys.exit(1)

def get_bucket(conn, url):
    bucket, path = parse_url(url)
    s3bucket = conn.get_bucket(bucket)

    if s3bucket:
        return s3bucket
    else:
        logging.error("Bucket: <%s> does not exist" % bucket)
        sys.exit(1)

def get_key(s3bucket, url):
    bucket, path = parse_url(url)
    key = s3bucket.get_key(path)

    if key:
        return key
    else:
        logging.error("File not found: %s" % (url))
        sys.exit(1)

def get_file(key, url, filename):
    logging.info("Downloading file %s -> %s" % (url, filename))
    with open(filename, 'w') as f:
        key.get_file(f)

def run():
    (accesskey, secretkey) = get_creds()
    args = get_args()
    numeric_level = get_numeric_loglevel(args.loglevel)
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=numeric_level)
    conn = get_conn(accesskey, secretkey)

    bucket = get_bucket(conn, args.url)
    key = get_key(bucket, args.url)
    get_file(key, args.url, args.filename)

if __name__ == '__main__':
    run()
