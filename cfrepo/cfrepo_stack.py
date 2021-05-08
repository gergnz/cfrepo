"""CloudFormation Repository Hosting Stack"""
import os
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import (core, aws_s3 as s3,
                           aws_ec2 as ec2,
                           aws_ecs as ecs,
                           aws_iam as iam,
                           aws_route53 as r53,
                           aws_dynamodb as dynamodb,
                           aws_ecs_patterns as ecs_patterns,
                           aws_elasticloadbalancingv2 as elbv2)

dirname = os.path.dirname(__file__)

ZONEID=os.environ.get('ZONEID')
ZONENAME=os.environ.get('ZONENAME')

class CfrepoStack(core.Stack):
    """Core Stack"""
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, 'CfrVpc',
            max_azs=3,
            subnet_configuration=[ec2.SubnetConfiguration(
                cidr_mask=24,
                name='public',
                subnet_type=ec2.SubnetType.PUBLIC
            )],
            nat_gateways=0
        )

        table = dynamodb.Table(self, 'CfrTable',
            point_in_time_recovery=True,
            partition_key=dynamodb.Attribute(
                name="RepositoryURI",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="TemplatePATH",
                type=dynamodb.AttributeType.STRING
            )
        )

        cluster = ecs.Cluster(self, 'CfrCluster', vpc=vpc)

        asset = DockerImageAsset(self, 'cloudformationrepo',
            directory=os.path.join(dirname, '..', 'cloudformationrepo')
        )

        bucket = s3.Bucket(self, 'CfrBucket',
            enforce_ssl=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess(
                block_public_policy=True,
                restrict_public_buckets=True
            ),
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    abort_incomplete_multipart_upload_after=core.Duration.days(1),
                    noncurrent_version_expiration=core.Duration.days(1)
                )
            ]
        )

        task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
            container_port=5000,
            environment={
                'DYNAMODB_TABLE': table.table_name,
                'S3_BUCKET': bucket.bucket_name
            },
            image=ecs.ContainerImage.from_ecr_repository(
                asset.repository,
                asset.image_uri.rpartition(":")[-1]
            )
        )

        ecs_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, 'CfrService',
            cluster=cluster,
            assign_public_ip=True,
            task_image_options=task_image_options,
            public_load_balancer=True,
            domain_name='cfrepo.'+ZONENAME,
            domain_zone=r53.HostedZone.from_hosted_zone_attributes(self, 's2szone',
                hosted_zone_id=ZONEID,
                zone_name=ZONENAME
                ),
            protocol=elbv2.ApplicationProtocol.HTTPS,
            redirect_http=True
        )

        ecs_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=[
                    'dynamodb:BatchWriteItem',
                    'dynamodb:PutItem',
                    'dynamodb:Scan'
                ],
                resources=[table.table_arn]
            )
        )

        ecs_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                actions=[
                    's3:PutObject',
                    's3:PutObjectAcl',
                    's3:DeleteObject'
                ],
                resources=[bucket.bucket_arn + '/*']
            )
        )

        ecs_service.target_group.configure_health_check(
            interval=core.Duration.seconds(300)
        )
