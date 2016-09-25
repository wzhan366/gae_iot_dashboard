import boto
from boto.sqs.message import Message

def sqs_write(message):
    try:
        conn = boto.sqs.connect_to_region("us-west-2",
                        aws_access_key_id='your api_key_id',
                        aws_secret_access_key='your secret_access_key')
        #get queue by queue name
        my_queue = conn.get_queue('appEngine-rpi')
        m = Message()
        # print message
        m.set_body(message)
        ack = my_queue.write(m)
    except Exception as err:
        print err
