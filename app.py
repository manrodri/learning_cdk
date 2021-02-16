from aws_cdk import core
from stacks.vpc_stack import VPCStack
from stacks.security_stack import SecurityStack
from stacks.bastion_stack import BastionStack
from stacks.kms_stack import KMSStack
from stacks.s3_stack import S3Stack
from stacks.rds_stack import RDSStack
from stacks.cognito_stack import CognitoStack
from stacks.apigw_stack import APIStack
from stacks.lambda_stack import LambdaStack

app = core.App()

vpc_stack = VPCStack(app, 'vpc-stack', env={'region': 'eu-west-1'})
security_stack = SecurityStack(app, 'security-stack',
                               vpc=vpc_stack.vpc,
                               env={'region': 'eu-west-1'})
bastion_stack = BastionStack(app, 'bastion-stack',
                             vpc=vpc_stack.vpc,
                             sg=security_stack.bastion_sg,
                             env={'region': 'eu-west-1'})
kms_stack = KMSStack(app, 'kms-stack', env={'region': 'eu-west-1'})
s3_stack = S3Stack(app, 's3buckets', env={'region': 'eu-west-1'})
rds_stack = RDSStack(app, 'rds-stack',
                     vpc=vpc_stack.vpc,
                     bastionsg=security_stack.bastion_sg,
                     lambdasg=security_stack.lambda_sg,
                     kmskey=kms_stack.kms_rds,
                     env={'region': 'eu-west-1'})
cognito_stack = CognitoStack(app, 'cognito-stack', env={'region': 'eu-west-1'})
apigw_stack = APIStack(app, 'apigw-stack', env={'region': 'eu-west-1'})
lambda_stack = LambdaStack(app,'lambda-stack')

app.synth()
