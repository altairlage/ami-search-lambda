
def repoName = 'ami-search-lambda'
def gitHubUser = 'jenkins-gh'
def githubServerName = ''
def gitHubUrl = "https://${githubServerName}/${repoName}.git"

def branch = (env.BRANCH_NAME)
def environment = getEnvironmentFromBranch(branch)

node('ubuntu_bionic') {
    deleteDir()

    try {
        stage('Checkout') {
            checkOut(gitHubUrl, branch, gitHubUser)
        }

        stage('Zip Lambda') {
            dir('lambda') {
                def zipFile = "ami-search-${environment}.zip"
                sh("zip -r9 ${zipFile} ami_search.py")
            }
        }

        stage('Deploy Code') {
            if (fileExists('requirements.txt')) {
                sh('python3 -m pip install -r requirements.txt')
            }

            def regions = ['us-west-2', 'ap-northeast-1', 'eu-central-1']

            sts = getStsCreds(environment)
            withEnv(["AWS_ACCESS_KEY_ID=${sts[0]}", "AWS_SECRET_ACCESS_KEY=${sts[1]}", "AWS_SESSION_TOKEN=${sts[2]}"]) {
                for (region in regions) {
                    sh("python run.py --region ${region} --environment ${environment} --branch ${branch} --aws-access-key $AWS_ACCESS_KEY_ID  --aws-secret-key $AWS_SECRET_ACCESS_KEY --aws-session-token $AWS_SESSION_TOKEN")
                }
            }
        }
    } catch (e) {
        error(e.getMessage())
    } finally {
        deleteDir()
    }
}

def getEnvironmentFromBranch(branch) {
    def environmentMap = [
        'qa'      : 'qa',
        'staging' : 'staging',
        'master'  : 'prod'
    ]
    return environmentMap.get(branch, 'dev')
}

def checkOut(repo, branch, creds = 'jenkins-gh') {
    checkout(
        [
            $class: 'GitSCM',
            branches: [
                [
                    name: '*/' + branch
                ]
            ],
            doGenerateSubmoduleConfigurations: false,
            userRemoteConfigs: [
                [
                    credentialsId: creds,
                    url: repo
                ]
            ]
        ]
    )
}

def getAWSAccountId(environment) {
    file = new File('./deployment_helper/aws_accounts.json')
    json = new JsonSlurper().parse(file)

    accountId = json[environment]?.account

    println "Account for ${environment}: ${accountId}"
    return accountId
}

def getJenkinsRoleArn(String account) {
    return "arn:aws:iam::${account}:role/jenkins-role"
}

def Tuple getStsCreds(String environmentName) {
    String accountId = getAWSAccountId(environmentName)
    String roleArn = getJenkinsRoleArn(accountId)

    try {
        String cmd = "aws sts assume-role --role-arn ${roleArn} --role-session-name \"RoleSession1\" --output text" +
                " | awk 'END {print \$2 \"\\n\" \$4 \"\\n\" \$5}' > temp.txt"
        steps.sh(cmd)
    } catch (Exception e) {
        steps.println(e)
    }

    String key = steps.sh(returnStdout: true, script: 'head -1 temp.txt | tail -1 | tr -d "\n" ')
    String secret = steps.sh(returnStdout: true, script: 'head -2 temp.txt | tail -1 | tr -d "\n" ')
    String token = steps.sh(returnStdout: true, script: 'head -3 temp.txt | tail -1 | tr -d "\n" ')
    steps.sh('rm -f temp.txt')
    return [key, secret, token]
}
