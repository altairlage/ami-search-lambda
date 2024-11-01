import logging
import os
from os.path import join, dirname
import argparse

from deploy_helper import deployment_helper as helper

def main():
    # Setup Logging format & level
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('--region', '-r', type=str, required=True )
    parser.add_argument('--environment', '-e', type=str, required=True)
    parser.add_argument('--branch', '-br', type=str, required=True)
    parser.add_argument("--aws-access-key", required=False, help="AWS access key ID.")
    parser.add_argument("--aws-secret-key", required=False, help="AWS secret access key.")
    parser.add_argument("--aws-session-token", required=False, help="AWS session token.")

    args = parser.parse_args()

    aws_region = args.region.lower()
    aws_env = args.environment.lower()
    branch = args.branch.lower()
    aws_access_key = args.aws_access_key
    aws_secret_key = args.aws_secret_key
    aws_session_token = args.aws_session_token

    # AWS clients and resource setup
    aws_session = helper.get_aws_session(aws_access_key=aws_access_key, aws_secret_key=aws_secret_key, aws_session_token=aws_session_token, region=aws_region)
    cfn_client = helper.get_aws_client(client='cloudformation', session=aws_session)
    cfn_resource = helper.get_aws_resource(client='cloudformation', aws_access_key=aws_access_key, aws_secret_key=aws_secret_key, aws_session_token=aws_session_token, region=region)
    lambda_client = helper.get_aws_client(client='lambda', session=aws_session)
    s3_resource = helper.get_aws_resource(client='s3', session=aws_session)

    stack_root_name = "ami-search"

    if aws_env == 'prod':
        stack_name = f"{aws_region}-{stack_root_name}"
        lambda_name = f"{aws_region}-ami-search"
    else:
        stack_name = f"{aws_env}-{aws_region}-{stack_root_name}"
        lambda_name = f"{aws_env}-{aws_region}-ami-search"

    lambda_template = open(os.path.join(os.path.dirname(__file__), 'cfn', "lambda.yaml")).read()

    # Bucket Name
    lambda_bucket_name = f"{aws_region}-lambda-files"

    current_dir = dirname(__file__)
    script_name = "ami-search"
    src_dir = join(current_dir, 'lambda')

    zip_file_name = f"{script_name}-infra-{aws_env}.zip"
    zip_file_path = join(src_dir, zip_file_name)

    # Setup parameters for deployment
    lambda_params = [
        {"ParameterKey": "LambdaBucket", "ParameterValue": lambda_bucket_name},
        {"ParameterKey": "ZipName", "ParameterValue": zip_file_name},
        {"ParameterKey": "LambdaName", "ParameterValue": lambda_name}
    ]

    zip_file = open(zip_file_path, 'rb')
    s3_resource.Bucket(lambda_bucket_name).put_object(Key=zip_file_name, Body=zip_file)

    helper.create_or_update_stack(cf_client=cfn_client, stack_name=stack_name, template_body=lambda_template, parameters=lambda_params)

    account_id = helper.get_current_account_id(aws_session)

    helper.update_lambda(lambda_client=lambda_client, bucketname=lambda_bucket_name, filename=zip_file_name, accountid=account_id, lambdaname=lambda_name, region=aws_region)


if __name__ == '__main__':
    main()
