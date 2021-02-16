from aws_cdk import (
    aws_rds as rds,
    aws_ssm as ssm,
    aws_ec2 as ec2,
    aws_kms as kms,
    aws_secretsmanager as sm,
    core
)

import json

class RDSStack(core.Stack):

    def __init__(self,
                 scope:core.Construct,
                 id: str,
                 vpc:ec2.Vpc,
                 lambdasg:ec2.SecurityGroup,
                 bastionsg:ec2.SecurityGroup,
                 kmskey:kms.Key,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        db_mysql = rds.DatabaseCluster(self, 'mysql',
                                       default_database_name=prj_name + env_name,
                                       engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
                                       instance_props=rds.InstanceProps(
                                           vpc=vpc,
                                           vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED),
                                           instance_type=ec2.InstanceType(instance_type_identifier="t3.small")
                                       ),
                                       instances=1,
                                       storage_encrypted=True,
                                       storage_encryption_key=kmskey,
                                       removal_policy=core.RemovalPolicy.DESTROY
                                       )

        db_mysql.connections.allow_default_port_from(lambdasg, 'Allow from Lambda function')
        db_mysql.connections.allow_default_port_from(bastionsg, "Allow from bastion host")

        ssm.StringParameter(self, 'db-host',
                            parameter_name=f"/{env_name}/db-host",
                            string_value=db_mysql.cluster_endpoint.hostname)

