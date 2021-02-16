from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam,
    core

)


class SecurityStack(core.Stack):

    def __init__(self, scope:core.Construct, id:str, vpc:ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        self.lambda_sg = ec2.SecurityGroup(self, 'lambdasg',
                                      security_group_name='lambda-sg',
                                      vpc=vpc,
                                      description='security group for lambda functions',
                                      allow_all_outbound=True)

        self.bastion_sg = ec2.SecurityGroup(self, 'bastion-sg',
                                       security_group_name='bastion_sg',
                                       vpc=vpc,
                                       description='sg for bastion host',
                                       allow_all_outbound=True)
        self.bastion_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description='SSH Access for bastion host'
        )

        lambda_role = iam.Role(self, 'lambda-role',
                               assumed_by=iam.ServicePrincipal(service='lambda.amazonaws.com'),
                               role_name='lambda-role',
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name(
                                       managed_policy_name='service-role/AWSLambdaBasicExecutionRole'
                                   )
                               ])
        lambda_role.add_to_policy(
            statement=iam.PolicyStatement(
                actions=['s3:*', 'rds:*'],
                resources=['*']

            )
        )

        # Create SSM params
        ssm.StringParameter(self, 'lambdasg-param',
                            parameter_name=f'/{env_name}/lambda-sg',
                            string_value=self.lambda_sg.security_group_id
                            )
        ssm.StringParameter(self,'lambdarolearn-param',
                            parameter_name=f'/{env_name}/lambda-role-arn',
                            string_value=lambda_role.role_arn)
        ssm.StringParameter(self, 'lambdarolename-param',
                            parameter_name=f'/{env_name}/lambda-role-name',
                            string_value=lambda_role.role_name)





