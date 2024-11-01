import json
import logging
import boto3

logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    ec2_client = boto3.client("ec2", region_name=event["aws_region"])

    # Generate the ami_name - wildcard the version, if any, and the timestamp
    ami_name = event["aws_region"] + "-" + event["ami_type"] + "-*"
    state = event.get("ami_state", "prod")

    registered_amis = ec2_client.describe_images(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    ami_name
                ]
            },
            {
                'Name': 'tag:release-state',
                'Values': [
                    state
                ]
            }
        ]
    )

    if not registered_amis or not registered_amis['Images']:
        if _get_api_version(event) == 2:
            return []
        else:
            return {"Name": "no-ami-found", "ami": "no-ami-found"}

    ami_dict = {ami['Name']: ami['ImageId'] for ami in registered_amis['Images']}
    sorted_ami_list = [
        {'Name': name, 'ami': ami} for name, ami in sorted(ami_dict.items(), reverse=True)
    ]

    if _get_api_version(event) == 2:
        return sorted_ami_list
    else:
        return sorted_ami_list[0]


def _get_api_version(event):
    if event.get("get_all", False) is True:
        return 2
    else:
        return 1
