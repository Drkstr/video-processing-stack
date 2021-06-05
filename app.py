#!/usr/bin/env python3
import os
from aws_cdk import core as cdk

from video_processing_test.video_processing_test_stack import VideoProcessingTestStack


app = cdk.App()
VideoProcessingTestStack(app, "VideoProcessingTestStack")

app.synth()
