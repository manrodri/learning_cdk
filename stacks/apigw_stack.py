from aws_cdk import (
    aws_ssm as ssm,
    aws_apigateway as apigw,
    core
)


class APIStack(core.Stack):

    def __init__(self, scope:core.Construct, id:str, **kwargs)-> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        account_id = core.Aws.ACCOUNT_ID
        region = core.Aws.REGION

        api_gateway = apigw.RestApi(self, 'rest-api',
                                    endpoint_types=[apigw.EndpointType.REGIONAL],
                                    rest_api_name=f'{prj_name}-service')
        api_gateway.root.add_method(http_method='ANY')

        ssm.StringParameter(self, 'api-gw',
                            parameter_name=f'/{env_name}/api-gw-url',
                            string_value=f'https://{api_gateway.rest_api_id}.execute-api.{region}.amazonaws.com/')
        ssm.StringParameter(self,'api-gw-id',
                            parameter_name=f'/{env_name}/api-gw-id',
                            string_value=api_gateway.rest_api_id)

