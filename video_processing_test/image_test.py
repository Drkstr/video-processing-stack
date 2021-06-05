#!/usr/bin/env python3

from boto3 import resource
from os import getenv
from time import sleep
from random import randrange
from sys import argv
import numpy
import cv2
import pyzed.sl as sl


def get_queue_details():
    sqs = resource('sqs', region_name='ap-southeast-2')
    print(getenv('QUEUE_NAME'))
    return sqs.get_queue_by_name(QueueName=getenv('QUEUE_NAME'))


def receive():
    queue = get_queue_details()
    while True:
        for message in queue.receive_messages(MaxNumberOfMessages=10):
            print("MESSAGE CONSUMED: {}".format(message.body))
            print(message.delete())
            sleep(1)


def send(num_messages=500):
    queue = get_queue_details()
    for _num in range(num_messages):
        _rand = randrange(1000)
        print(queue.send_message(MessageBody=str(_rand)))


if __name__ == '__main__':
    try:
        print("NumPy version " + numpy.__version__)
        print("Open CV version " + cv2.__version__)
        print("ZED SDK version " + sl.__version__)
    except Exception as e:
        print(str(e))
        exit(200)
# if __name__ == '__main__':
#     try:
#         if argv[1] == 'send':
#             send()
#         if argv[1] == 'receive':
#             receive()
#     except IndexError as i:
#         print("Please pass either send or receive.\n./queue_service.py <send> <receive>")
#         exit(200)
