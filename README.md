# ami-search-lambda
![Amazon Web Services Badge](https://img.shields.io/badge/Amazon%20Web%20Services-232F3E?logo=amazonwebservices&logoColor=fff&style=for-the-badge)
![Lambda](https://img.shields.io/badge/AWS%20Lambda-FF9900.svg?style=for-the-badge&logo=AWS-Lambda&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![YAML](https://img.shields.io/badge/yaml-%23ffffff.svg?style=for-the-badge&logo=yaml&logoColor=151515)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939.svg?style=for-the-badge&logo=Jenkins&logoColor=white)
![Groovy](https://img.shields.io/badge/Apache%20Groovy-4298B8.svg?style=for-the-badge&logo=Apache-Groovy&logoColor=white)


This code deploy an AWS Lambda function. The deployment is done via CloudFormation, automated using Jenkins (Groovy) and Python.

This Lambda will return the newest AMI for EC2 or ECS based on the AMI info and release-state tag. It retrieves Amazon Machine Images (AMIs) based on specific criteria and tags, facilitating dynamic management and access to a list of AMIs or a single, most recent AMI. This can be particularly useful for environments where AMIs are frequently updated and need to be programmatically identified by filters and tags.

The `ami_name` variable is constructed dynamically based on the region and AMI type from the event. The `ami_state` (release state) defaults to "prod" unless otherwise provided.

Using the `describe_images` method, the function searches for AMIs with a name matching the wildcard pattern and a specific `release-state` tag. The results are stored in `registered_amis`, which contains metadata about matching images.

If no AMIs match the criteria, the function checks the API version using `_get_api_version`. Depending on this version:

Version 2 (get_all=True): Returns an empty list.
Version 1 (get_all=False): Returns a dictionary indicating no AMI was found.

## Usage Example

**Event data example:**
    {
        "aws_region": "us-west-2",
        "ami_type": "ecs",
        "ami_state": "prod",
        "get_all": true
    }

**Possible Outputs:**

1. If AMIs are found:
    - get_all=True: Returns a list of all AMIs, each entry containing Name and ami.
    - get_all=False: Returns only the latest AMI with its Name and ami.
1. If no AMIs match:
    - get_all=True: Returns an empty list.
    - get_all=False: Returns { "Name": "no-ami-found", "ami": "no-ami-found" }.