from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codepipeline_actions as cp_actions,
    aws_codecommit as ccm,
    aws_iam as iam,
    core
)


class CodePipelineFrontendStack(core.Stack):
    def __init__(self, scope:core.Construct, id:str, frontendBucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context('project_name')
        env_name = self.node.try_get_context('env')

        webhosting_buket = s3.Bucket.from_bucket_name(self, 'webhostingbucket-id', bucket_name=frontendBucket)
        cdn_id = ssm.StringParameter.from_string_parameter_name(self, 'cdn_id', string_parameter_name=f'/{env_name}/cdn-id')

        source_repo = ccm.Repository.from_repository_name(self, 'repository-id', repository_name='cdk_app_frontend')

        artifact_bucket = s3.Bucket(self, 'artifactbucket',
                                    encryption=s3.BucketEncryption.S3_MANAGED,
                                    access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL
                                    )
        pipeline = cp.Pipeline(self, 'frontend-pipeline',
                               pipeline_name=f'{prj_name}-{env_name}-frontend-pipeline',
                               artifact_bucket=artifact_bucket,
                               restart_execution_on_update=False
                               )
        source_output = cp.Artifact(artifact_name='source')
        build_output = cp.Artifact(artifact_name='build')

        pipeline.add_stage(stage_name='Source',
                           actions=[
                               cp_actions.CodeCommitSourceAction(
                                   action_name='CodeCommitSource',
                                   repository=source_repo,
                                   branch='master',
                                   output=source_output
                               )
                           ])








