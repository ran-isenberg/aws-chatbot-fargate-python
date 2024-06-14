from aws_cdk import Aspects, Stack, Tags
from cdk_nag import AwsSolutionsChecks, NagSuppressions
from constructs import Construct

from cdk.service.chat_bot_construct import ChatBot
from cdk.service.constants import OWNER_TAG, SERVICE_NAME, SERVICE_NAME_TAG
from cdk.service.network_assets_construct import ChatNetworkAssets
from cdk.service.utils import get_username
from cdk.service.waf_construct import WafToAblConstruct


class ServiceStack(Stack):
    def __init__(self, scope: Construct, id: str, is_production_env: bool, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._add_stack_tags()

        self.network_assets = ChatNetworkAssets(self, 'NetworkAssets')

        self.waf = WafToAblConstruct(self, 'WafToAbl')

        self.api = ChatBot(
            self,
            'ChatBot',
            waf_acl=self.waf.web_acl,
            network_assets=self.network_assets,
        )

        # add security check
        self._add_security_tests()

    def _add_stack_tags(self) -> None:
        # best practice to help identify resources in the console
        Tags.of(self).add(SERVICE_NAME_TAG, SERVICE_NAME)
        Tags.of(self).add(OWNER_TAG, get_username())

    def _add_security_tests(self) -> None:
        Aspects.of(self).add(AwsSolutionsChecks(verbose=True))
        # Suppress a specific rule for this resource
        NagSuppressions.add_stack_suppressions(
            self,
            [
                {'id': 'AwsSolutions-IAM4', 'reason': 'policy for cloudwatch logs.'},
                {'id': 'AwsSolutions-IAM5', 'reason': 'policy for cloudwatch logs.'},
                {'id': 'AwsSolutions-APIG2', 'reason': 'lambda does input validation'},
                {'id': 'AwsSolutions-APIG1', 'reason': 'not mandatory in a sample template'},
                {'id': 'AwsSolutions-APIG3', 'reason': 'not mandatory in a sample template'},
                {'id': 'AwsSolutions-APIG6', 'reason': 'not mandatory in a sample template'},
                {'id': 'AwsSolutions-APIG4', 'reason': 'authorization not mandatory in a sample template'},
                {'id': 'AwsSolutions-COG4', 'reason': 'not using cognito'},
                {'id': 'AwsSolutions-L1', 'reason': 'False positive'},
                {'id': 'AwsSolutions-VPC7', 'reason': 'Not interested in this check'},
                {'id': 'AwsSolutions-EC23', 'reason': 'False positive, port is limited to 80 or 443'},
            ],
        )
