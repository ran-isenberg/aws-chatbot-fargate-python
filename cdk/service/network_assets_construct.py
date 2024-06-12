from aws_cdk import aws_certificatemanager as acm

from aws_cdk import aws_route53 as route53
from aws_cdk import aws_wafv2 as wafv2
from constructs import Construct


class ChatNetworkAssets(Construct):
    def __init__(self, scope: Construct, identifier: str) -> None:
        super().__init__(scope, identifier)
        self.id_ = identifier

        # Parameters
        self.domain_name = 'ranthebuilderapps.com'
        self.subdomain_name = 'chat'
        self.full_domain = f'{self.subdomain_name}.{self.domain_name}'

        # Load existing hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(self, 'HostedZone', domain_name=self.domain_name)

        # Create a certificate for the subdomain
        self.certificate = acm.Certificate(
            self,
            'ChatBotCertificate',
            domain_name=self.full_domain,
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
        )

    def register_target_to_subdomain(self, target: route53.RecordTarget) -> None:
        # Create Route 53 A record for the subdomain
        self.subdomain_route = route53.ARecord(
            self,
            'ChatAliasRecord',
            zone=self.hosted_zone,
            target=target,
            record_name=self.full_domain,
        )
