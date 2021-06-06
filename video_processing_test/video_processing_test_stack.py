from aws_cdk import core as cdk
from aws_cdk.aws_ec2 import Vpc, InstanceType
from aws_cdk.aws_ecs import ContainerImage, Cluster
from aws_cdk.aws_ecs_patterns import QueueProcessingEc2Service
from aws_cdk.aws_s3 import Bucket, NotificationKeyFilter, EventType
from aws_cdk.aws_s3_notifications import SqsDestination
from aws_cdk.aws_sqs import Queue, DeadLetterQueue


class VideoProcessingTestStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        _queue_name = "video-processing-queue"

        _vide_processing_dead_letter_queue: Queue = Queue(self,
                                                          _queue_name + "-DLQ",
                                                          queue_name=_queue_name + "-DLQ")

        _dead_letter_queue: DeadLetterQueue = DeadLetterQueue(max_receive_count=3,
                                                              queue=_vide_processing_dead_letter_queue)

        _video_processing_queue: Queue = Queue(self,
                                               _queue_name,
                                               queue_name=_queue_name,
                                               dead_letter_queue=_dead_letter_queue)

        _s3_notification_filter: NotificationKeyFilter = NotificationKeyFilter(prefix="asset/", suffix=".svo")

        _bucket_name = "com.leading-edge.video-test-bucket"

        _video_source_bucket: Bucket = Bucket(self, _bucket_name, bucket_name=_bucket_name)

        _video_source_bucket.add_event_notification(
            EventType.OBJECT_CREATED_PUT,
            SqsDestination(_video_processing_queue),
            _s3_notification_filter
        )

        _container_image: ContainerImage = ContainerImage.from_asset(
            directory=".",
            file='Dockerfile.Video_Processor',
            exclude=["cdk.out"]
        )

        _scaling_steps = [{"upper": 0, "change": -1}, {"lower": 50, "change": +1}, {"lower": 100, "change": +2}]

        _vpc: Vpc = Vpc(self, "video-processing-vpc", max_azs=3)

        _cluster_name = "video-processing-cluster"

        _cluster = Cluster(self, "video-processing-cluster", vpc=_vpc, cluster_name=_cluster_name)

        _cluster.add_capacity("video-processing-autoscaling-capacity",
                              instance_type=InstanceType("g4dn.xlarge"),
                              min_capacity=1,
                              max_capacity=3)

        _video_processing_service_name = "Video Processing Cluster"
        self.videoProcessingService = QueueProcessingEc2Service(
            self,
            _video_processing_service_name,
            service_name=_video_processing_service_name,
            cluster=_cluster,
            cpu=512,
            scaling_steps=_scaling_steps,
            memory_limit_mib=1024,
            image=_container_image,
            min_scaling_capacity=1,
            max_scaling_capacity=5,
            queue=_video_processing_queue
        )
