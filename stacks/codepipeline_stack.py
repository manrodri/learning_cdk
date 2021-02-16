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





