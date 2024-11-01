import boto3
import botocore
import yaml
import os

def read_file(*fileargs):
    """
    Read the contents of a file and return the contents. The fileargs
    is a list of path components to be added to the current directory
    """
    path = os.path.join(*fileargs)
    data = open(path).read()
    return data


def get_aws_session(aws_access_key, aws_secret_key, aws_session_token, region):
    # session = boto3.Session(
    session = boto3.session.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_session_token,
        region_name=region
    )
    return session


def get_aws_resource(client, session):
    return session.resource(client)


def get_aws_client(client, session):
    return session.client(client)


def get_current_account_id(session):
    sts = session.client('sts')
    return sts.get_caller_identity()["Account"]


def _gen_param_list(params):
    """Convert a dictionary to a parameter list used by AWS APIs"""
    param_list = []
    for key, value in params.items():
        param_list.append({"ParameterKey": key, "ParameterValue": value})
    return param_list


def create_or_update_stack(cf_client, stack_name, template_body, parameters):
    """Create or update a CloudFormation stack."""
    try:
        # Check if stack exists
        cf_client.describe_stacks(StackName=stack_name)
        
        # If it exists, update it
        print(f"Updating the {stack_name} stack...")
        response = cf_client.update_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        print(f"Update initiated: {response['StackId']}")
    except botocore.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            # If it doesn't exist, create it
            print(f"Creating the {stack_name} stack...")
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
            print(f"Creation initiated: {response['StackId']}")
        elif 'No updates are to be performed' in str(e):
            print("No updates needed for the stack.")
        else:
            raise


def update_lambda(lambda_client, bucketname, filename, accountid, lambdaname, region):
    try:
        lambda_client.update_function_code(
            FunctionName="arn:aws:lambda:" + region + ":" + accountid + ":function:" + lambdaname,
            S3Bucket=bucketname,
            S3Key=filename
        )
        return True
    except botocore.exceptions.ClientError as e:
        return False