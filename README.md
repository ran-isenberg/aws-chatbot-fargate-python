# ChatBot AWS CDK Deployment

[![license](https://img.shields.io/github/license/ran-isenberg/aws-chatbot-fargate-python)](https://github.com/ran-isenberg/aws-chatbot-fargate-python/blob/master/LICENSE)
![PythonSupport](https://img.shields.io/static/v1?label=python&message=3.12&color=blue?style=flat-square&logo=python)
![version](https://img.shields.io/github/v/release/ran-isenberg/aws-chatbot-fargate-python)
![github-star-badge](https://img.shields.io/github/stars/ran-isenberg/aws-chatbot-fargate-python.svg?style=social)
![issues](https://img.shields.io/github/issues/ran-isenberg/aws-chatbot-fargate-python)

![alt text](https://github.com/ran-isenberg/aws-chatbot-fargate-python/blob/main/docs/media/banner.png?raw=true)

This project deploys an AWS Fargate-based ESC cluster web application using AWS CDK (Cloud Development Kit).

The infrastructure includes an ECS cluster, Fargate service, Application Load Balancer, VPC, and WAF and includes security best practices with CDK-nag verification.

The web application is a chatbot but can replaced to any application you wish.

The chatbot is based on an implementation by [Streamlit](https://streamlit.io/) and the initial prompt is that the chatbot is me, Ran the builder, a serverless hero and attempts to answer as me.

The Chatbot uses custom domain (you can remove it or change it to your own domain) and assume an OpenAI token exists in the account in the form of a secrets manager secret for making API calls to OpenAI.

**[Blogs website](https://www.ranthebuilder.cloud)** > **Contact details | ran.isenberg@ranthebuilder.cloud**

[![Twitter Follow](https://img.shields.io/twitter/follow/IsenbergRan?label=Follow&style=social)](https://twitter.com/IsenbergRan)
[![Website](https://img.shields.io/badge/Website-www.ranthebuilder.cloud-blue)](https://www.ranthebuilder.cloud/)


## Prerequisites

- AWS CLI configured with appropriate credentials
- Node.js (with npm)
- Python 3.12 or higher
- AWS CDK 2.149.0 or greater installed
- OpenAI API key deployed as a secret (see cdk/service/Docker/app.py)

## Project Structure

- `cdk.service.network_assets_construct`: Custom construct for network-related resources.
- `docker/`: Directory containing the Dockerfile for the chat application.
- `app.py`: Entry point for the CDK application.
- `chat_bot_construct.py` - the Fargate construct

## CDK Stack Overview

### Resources Created

- **VPC**: Virtual Private Cloud with 2 Availability Zones.
- **ECR**: Amazon Elastic Container Registry to store Docker images.
- **ECS Cluster**: Elastic Container Service cluster with Fargate capacity providers.
- **Fargate Task Definition**: Defines the container specifications.
- **Fargate Service**: Deploys the container and integrates with the Application Load Balancer.
- **Application Load Balancer**: Publicly accessible load balancer with SSL termination.
- **WAF**: Web Application Firewall to protect the application.
- **S3 Buckets**: Used for access logs with encryption and secure settings.
- **IAM Roles and Policies**: Permissions for ECS tasks and other services.
- **Auto Scaling**: CPU and memory-based auto-scaling configuration.

## Deployment

### Step 1: Install Dependencies

Navigate to your project directory and install the necessary dependencies:

```bash
cd {new repo folder}
poetry shell
poetry install
make deploy
```

You can also run 'make pr' will run all checks, synth, file formatters and deploy to AWS.

## Code Contributions

Code contributions are welcomed. Read this [guide.](https://github.com/ran-isenberg/aws-chatbot-fargate-python/blob/main/CONTRIBUTING.md)

## Code of Conduct

Read our code of conduct [here.](https://github.com/ran-isenberg/aws-chatbot-fargate-python/blob/main/CODE_OF_CONDUCT.md)

## Connect

- Email: [ran.isenberg@ranthebuilder.cloud](mailto:ran.isenberg@ranthebuilder.cloud)
- Blog Website [RanTheBuilder](https://www.ranthebuilder.cloud)
- LinkedIn: [ranisenberg](https://www.linkedin.com/in/ranisenberg/)
- Twitter: [IsenbergRan](https://twitter.com/IsenbergRan)

## Credits

- [AWS Lambda Powertools (Python)](https://github.com/aws-powertools/powertools-lambda-python)

## License

This library is licensed under the MIT License. See the [LICENSE](https://github.com/ran-isenberg/aws-chatbot-fargate-python/blob/main/LICENSE) file.
