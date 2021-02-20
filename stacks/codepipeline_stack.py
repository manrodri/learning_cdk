from aws_cdk import (
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as cb,
    aws_ssm as ssm,
    aws_secretsmanager as sm,
    aws_iam as iam,
    aws_s3 as s3,
    core

)

class CodePipelineBackendStack(core.Stack):

    def __init__(self, scope:core.Construct, id:str, artifactbucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        artifact_bucket = s3.Bucket.from_bucket_name(self, 'artifactbucket', artifactbucket)
        github_token = core.SecretValue.secrets_manager(
            secret_id=f'{env_name}/github-token', json_field='github-token'
        )

        pipeline = cp.Pipeline(self, 'backend-pipeline',
                               pipeline_name=f'{env_name}-{prj_name}-backend-pipeline',
                               artifact_bucket=artifact_bucket,
                               restart_execution_on_update=False,
                               )

        source_output = cp.Artifact(artifact_name='source')
        build_output = cp.Artifact(artifact_name='build')

        build_project = cb.Project(self, 'buildproject',
                                   project_name=f'{env_name}-{prj_name}-build-project',
                                   description='package lambda functions',
                                   environment=cb.BuildEnvironment(
                                       build_image=cb.LinuxBuildImage.STANDARD_3_0,
                                       environment_variables={
                                           'ENV': cb.BuildEnvironmentVariable(value='dev'),
                                           'PRJ': cb.BuildEnvironmentVariable(value=prj_name),
                                           'STAGE': cb.BuildEnvironmentVariable(value='dev')
                                       }
                                   ),
                                   build_spec=cb.BuildSpec.from_object(
                                       {
                                           'version': '0.2',
                                           'phases': {
                                               'install': {
                                                   'commands': [
                                                       'echo --INSTALL PHASE--',
                                                       'npm install --silent --no-progress serverless -g'
                                                   ]
                                               },
                                               'pre_build': {
                                                   'commands': [
                                                       'echo --PRE BUILD PHASE--',
                                                       'npm install --silent --no-progress'
                                                   ]
                                               },
                                               'build': {
                                                   'commands': [
                                                       'echo --BUILD PHASE--',
                                                       'serverless deploy -s $STAGE'
                                                   ]
                                               }
                                           },
                                           'artifacts': {
                                               'files': ["**/*"],
                                               'base-directory': '.serverless'
                                           }
                                       }
                                   )
                                   )

        pipeline.add_stage(stage_name='Source',
                           actions=[
                               cp_actions.GitHubSourceAction(
                                   oauth_token=github_token,
                                   output=source_output,
                                   repo='serverless_hello_world',
                                   branch='master',
                                   owner='manrodri',
                                   action_name='GitHubSource'
                               )
                           ])

        pipeline.add_stage(
            stage_name='Deploy',
            actions=[
                cp_actions.CodeBuildAction(
                    action_name='DeployToDev',
                    input=source_output,
                    project=build_project,
                    outputs=[build_output]
                )
            ]
        )

        # build_project.role.add_to_policy(iam.PolicyStatement(
        #     actions=['cloudformation:*', 's3:*', 'iam:*', 'lambda:*', 'apigateway:*'],
        #     resources=["*"]
        # ))

        build_project.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess')
        )

        account_id = core.Aws.ACCOUNT_ID
        region = core.Aws.REGION

        ## ssm params
        ssm.StringParameter(self, 'account-id', parameter_name=f'/{env_name}/account-id', string_value=account_id)
        ssm.StringParameter(self, 'region', parameter_name=f'/{env_name}/region', string_value=region)













