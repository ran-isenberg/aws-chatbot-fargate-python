from pathlib import Path

from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_wafv2 as wafv2
from constructs import Construct

from cdk.service.network_assets_construct import ChatNetworkAssets


class ChatBot(Construct):
    def __init__(self, scope: Construct, identifier: str, waf_acl: wafv2.CfnWebACL, network_assets: ChatNetworkAssets) -> None:
        super().__init__(scope, identifier)
        self.id_ = identifier
        self.network_assets = network_assets
        # Build Docker image and push to ECR

        current = Path(__file__).parent
        docker_dir = str(Path(current / 'docker'))
        docker_image_asset = ecr_assets.DockerImageAsset(
            self,
            'ChatDockerImage',
            directory=docker_dir,  # Directory with Dockerfile
        )

        # Create a VPC
        vpc = ec2.Vpc(self, 'ChatVpc', max_azs=2)

        # Create an ECS cluster
        cluster = ecs.Cluster(self, 'ChatCluster', vpc=vpc, container_insights=True, enable_fargate_capacity_providers=True)

        # Define an ECS task definition with a single container
        task_definition = ecs.FargateTaskDefinition(
            self,
            'ChatTaskDef',
            memory_limit_mib=512,
            cpu=256,
            runtime_platform=ecs.RuntimePlatform(
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
                cpu_architecture=ecs.CpuArchitecture.ARM64,
            ),
        )

        # Add container to the task definition
        container = task_definition.add_container(
            'ChatBotContainer',
            image=ecs.ContainerImage.from_docker_image_asset(docker_image_asset),
            logging=ecs.LogDrivers.aws_logs(stream_prefix='Chatbot', log_retention=logs.RetentionDays.ONE_DAY),
        )

        # Open the necessary port internally
        container.add_port_mappings(ecs.PortMapping(container_port=8501, protocol=ecs.Protocol.TCP))

        # Security group for the Fargate service
        security_group = ec2.SecurityGroup(self, 'ChatSecurityGroup', vpc=vpc)

        # Allow inbound traffic on ports 80 (HTTP) and 443 (HTTPS) from any IP
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'Allow HTTP traffic from the internet')
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), 'Allow HTTPS traffic from the internet')
        security_group.add_ingress_rule(ec2.Peer.any_ipv6(), ec2.Port.tcp(80), 'Allow HTTP traffic from the internet (IPv6)')
        security_group.add_ingress_rule(ec2.Peer.any_ipv6(), ec2.Port.tcp(443), 'Allow HTTPS traffic from the internet (IPv6)')

        access_logs_bucket = s3.Bucket(
            scope=self,
            id='accessLogsS3Bucket',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,  # removal_policy=RemovalPolicy.RETAIN,
            versioned=False,
            auto_delete_objects=True,  # False in production
            enforce_ssl=True,
        )

        log_bucket = s3.Bucket(
            scope=self,
            id='ALBAccessLogsBucket',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,  # removal_policy=RemovalPolicy.RETAIN,
            server_access_logs_bucket=access_logs_bucket,
            server_access_logs_prefix='chatbot-bucket/serverAccessLogging',
            versioned=False,
            auto_delete_objects=True,  # False in production
            enforce_ssl=True,
        )

        # Create a Fargate service and make it publicly accessible
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            'ChatFargateService',
            cluster=cluster,
            task_definition=task_definition,
            assign_public_ip=False,
            public_load_balancer=True,
            listener_port=443,
            certificate=self.network_assets.certificate,
            domain_name=self.network_assets.full_domain,
            domain_zone=route53.HostedZone.from_lookup(self, 'BaseZone', domain_name=self.network_assets.domain_name),
            desired_count=1,
            security_groups=[security_group],
            load_balancer_name='chatbot-application-lb',
            redirect_http=True,
            circuit_breaker=ecs.DeploymentCircuitBreaker(enable=True, rollback=True),
            capacity_provider_strategies=[
                # ecs.CapacityProviderStrategy(capacity_provider='FARGATE_SPOT', weight=1), # not supported for ARM64
                ecs.CapacityProviderStrategy(capacity_provider='FARGATE', weight=1),
            ],
        )

        # Add policies to task role to allow bedrock API calls
        fargate_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['bedrock:*'],
                resources=['*'],
            )
        )

        fargate_service.task_definition.add_to_task_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=['secretsmanager:GetSecretValue'],
                resources=['*'],  # place secret ARN here
            )
        )

        # Enable access logging
        fargate_service.load_balancer.log_access_logs(log_bucket)

        # Associate the WAF web ACL with the ALB
        wafv2.CfnWebACLAssociation(
            self, 'ChatWebACLAssociation', resource_arn=fargate_service.load_balancer.load_balancer_arn, web_acl_arn=waf_acl.attr_arn
        )

        # Limit scaling to one container
        # Auto-scaling for the ECS service
        scalable_target = fargate_service.service.auto_scale_task_count(min_capacity=1, max_capacity=2)

        scalable_target.scale_on_cpu_utilization(
            'CpuScaling',
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        scalable_target.scale_on_memory_utilization('MemoryScaling', target_utilization_percent=80)

        # Ensure the load balancer is deleted when the stack is destroyed
        fargate_service.load_balancer.apply_removal_policy(RemovalPolicy.DESTROY)
        # add health check
        fargate_service.target_group.configure_health_check(path='/healthz', interval=Duration.seconds(60), timeout=Duration.seconds(5), enabled=True)
