from aws_cdk import (
    aws_iam as iam,
    aws_ssm as ssm,
    aws_cognito as cg,
    core
)


class CognitoStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        user_pool = cg.CfnUserPool(self, 'cognito_user_pool',
                                   auto_verified_attributes=['email'],
                                   username_attributes=['email', 'phone_number'],
                                   user_pool_name=f'{prj_name}-user-pool',
                                   schema=[
                                       {
                                           "attributeDataType": 'String',
                                           "name": "param1",
                                           "mutable": True
                                       }
                                   ],
                                   policies=cg.CfnUserPool.PoliciesProperty(
                                       password_policy=cg.CfnUserPool.PasswordPolicyProperty(
                                           minimum_length=10,
                                           require_lowercase=True,
                                           require_numbers=True,
                                           require_symbols=True,
                                           require_uppercase=True
                                       )
                                   )
                                   )
        user_pool_client = cg.CfnUserPoolClient(self, 'pool_client',
                                                user_pool_id=user_pool.ref,
                                                client_name=f'{env_name}-app-client')

        identity_pool = cg.CfnIdentityPool(self, 'identity_pool',
                                           allow_unauthenticated_identities=False,
                                           cognito_identity_providers=[
                                               cg.CfnIdentityPool.CognitoIdentityProviderProperty(
                                                   client_id=user_pool_client.ref,
                                                   provider_name=user_pool.attr_provider_name
                                               )
                                           ],
                                           identity_pool_name=f'{prj_name}-identity-pool'
                                           )

        ssm.StringParameter(self, 'app-id',
                            parameter_name=f'/{env_name}/cognito-app-client-id',
                            string_value=user_pool_client.ref)
        ssm.StringParameter(self, 'user-pool-id',
                            parameter_name=f'/{env_name}/cognito-user-pool-id',
                            string_value=user_pool.ref)
        ssm.StringParameter(self, 'identity-pool-id',
                            parameter_name=f'/{env_name}/cognito-identity-pool-id',
                            string_value=identity_pool.ref)

