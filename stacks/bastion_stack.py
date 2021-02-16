from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    core
)

class BastionStack(core.Stack):

    def __init__(self, scope:core.Construct, id:str, vpc:ec2.Vpc, sg:ec2.SecurityGroup, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        bastion_host = ec2.Instance(self, 'bastion-host',
                                    instance_type=ec2.InstanceType(instance_type_identifier='t2.micro'),
                                    machine_image=ec2.AmazonLinuxImage(
                                        edition=ec2.AmazonLinuxEdition.STANDARD,
                                        generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                                        virtualization=ec2.AmazonLinuxVirt.HVM,
                                        storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
                                        ),
                                    vpc=vpc,
                                    key_name='devops-cdk',
                                    vpc_subnets=ec2.SubnetSelection(
                                        subnet_type=ec2.SubnetType.PUBLIC
                                        ),
                                    security_group=sg
                                    )