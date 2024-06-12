from aws_cdk import aws_wafv2 as waf
from constructs import Construct


class WafToAblConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create WAF WebACL with AWS Managed Rules
        self.web_acl = waf.CfnWebACL(
            self,
            'ChatBotWebAcl',
            scope='REGIONAL',  # Change to CLOUDFRONT if you're using edge-optimized API
            default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
            name=f'{id}-Waf',
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True, cloud_watch_metrics_enabled=True, metric_name='ChatBotWebAcl'
            ),
            rules=[
                waf.CfnWebACL.RuleProperty(
                    name='Product-AWSManagedRulesCommonRuleSet',
                    priority=0,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesCommonRuleSet', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Chat-AWSManagedRulesCommonRuleSet',
                    ),
                ),
                # Block Amazon IP reputation list managed rule group
                waf.CfnWebACL.RuleProperty(
                    name='Chat-AWSManagedRulesAmazonIpReputationList',
                    priority=1,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesAmazonIpReputationList', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Chat-AWSManagedRulesAmazonIpReputationList',
                    ),
                ),
                # Block Anonymous IP list managed rule group
                waf.CfnWebACL.RuleProperty(
                    name='Chat-AWSManagedRulesAnonymousIpList',
                    priority=2,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesAnonymousIpList', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Product-AWSManagedRulesAnonymousIpList',
                    ),
                ),
                # rule for blocking known Bad Inputs
                waf.CfnWebACL.RuleProperty(
                    name='Chat-AWSManagedRulesKnownBadInputsRuleSet',
                    priority=3,
                    override_action={'none': {}},
                    statement=waf.CfnWebACL.StatementProperty(
                        managed_rule_group_statement=waf.CfnWebACL.ManagedRuleGroupStatementProperty(
                            name='AWSManagedRulesKnownBadInputsRuleSet', vendor_name='AWS'
                        )
                    ),
                    visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                        sampled_requests_enabled=True,
                        cloud_watch_metrics_enabled=True,
                        metric_name='Chat-AWSManagedRulesKnownBadInputsRuleSet',
                    ),
                ),
            ],
        )
