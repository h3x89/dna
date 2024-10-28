# Import necessary libraries from diagrams
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import Dynamodb, RDS
from diagrams.aws.network import APIGateway, ALB, Route53, VPC
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM, Cognito
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3
from diagrams.aws.devtools import Codepipeline
from diagrams.aws.general import User
from diagrams.onprem.client import Client

# Create the main diagram
with Diagram("Festival POS System Architecture", show=False):

    # Representing the festival attendee
    user = User("Festival Attendee")

    # POS Device used by the attendee, capable of offline transactions
    pos_device = Client("POS Device\n(Offline Capable)")

    # Begin the AWS Cloud cluster
    with Cluster("AWS Cloud"):

        # AWS Route 53 for DNS management and routing
        dns = Route53("DNS")

        # Virtual Private Cloud for networking
        with Cluster("VPC"):

            # Public Subnet containing internet-facing services
            with Cluster("Public Subnet"):

                # API Gateway as the entry point for all API calls from POS devices
                api_gateway = APIGateway("API Gateway")

                # Application Load Balancer to distribute traffic to microservices
                alb = ALB("Application Load Balancer")

            # Private Subnet containing backend services
            with Cluster("Private Subnet"):

                # Microservices cluster
                with Cluster("Microservices"):

                    # Authentication Service microservice
                    auth_service = Lambda("Auth Service")

                    # Transaction Processing Service microservice
                    transaction_service = Lambda("Transaction Service")

                    # User Management Service microservice
                    user_service = Lambda("User Management Service")

                    # Transaction History Service microservice
                    history_service = Lambda("Transaction History Service")

                # Databases cluster
                with Cluster("Databases"):

                    # Amazon DynamoDB with Global Tables for multi-region replication
                    dynamodb = Dynamodb("DynamoDB\n(Global Tables)")

                    # Amazon Aurora RDS (Relational Database Service)
                    rds = RDS("Aurora RDS")

            # Amazon S3 Bucket for storing backups and logs
            s3_bucket = S3("S3 Bucket\n(Backups & Logs)")

            # Amazon SQS Queue for message queuing (optional component)
            sqs_queue = SQS("SQS Queue")

            # AWS CloudWatch for monitoring and logging
            cloudwatch = Cloudwatch("CloudWatch")

        # AWS Identity and Access Management for roles and policies
        iam = IAM("IAM Roles & Policies")

        # AWS Cognito for user authentication and management
        cognito = Cognito("User Pool")

    # Define interactions and data flow

    # Festival attendee uses the POS device
    user >> pos_device

    # POS Device stores transactions offline when there's no internet
    pos_device - Edge(style="dashed", label="Stores Transactions\nOffline") - pos_device

    # When online, POS Device syncs with the API Gateway via HTTPS through DNS
    pos_device >> Edge(label="HTTPS", color="blue") >> dns >> api_gateway

    # API Gateway routes requests to the Application Load Balancer
    api_gateway >> alb

    # Load Balancer distributes traffic to the microservices
    alb >> auth_service
    alb >> transaction_service
    alb >> user_service
    alb >> history_service

    # Microservices interact with Amazon DynamoDB
    auth_service >> dynamodb
    transaction_service >> dynamodb
    user_service >> dynamodb
    history_service >> dynamodb

    # Transaction Service may also interact with Aurora RDS if needed
    transaction_service >> rds

    # Microservices send logs to AWS CloudWatch for monitoring
    [auth_service, transaction_service, user_service, history_service] >> cloudwatch

    # Back up databases to Amazon S3
    dynamodb >> Edge(color="darkgreen", style="dashed") >> s3_bucket
    rds >> Edge(color="darkgreen", style="dashed") >> s3_bucket

    # CloudWatch sends alerts to IAM roles or administrators
    cloudwatch >> Edge(label="Alerts", color="red") >> iam

    # API Gateway uses Cognito for user authentication
    api_gateway >> cognito

    # Cognito integrates with IAM for access control
    cognito >> iam

    # Continuous Integration/Continuous Deployment pipeline (optional component)
    codepipeline = Codepipeline("CI/CD Pipeline")

    # CI/CD Pipeline deploys updates to microservices
    codepipeline >> [auth_service, transaction_service, user_service, history_service]

    # POS Device may use SQS Queue for message queuing to the Transaction Service (optional)
    pos_device >> Edge(style="dotted") >> sqs_queue >> transaction_service

    # Indicate that services can auto-scale based on load
    autoscaling = Edge(label="Auto Scaling", style="dashed")
    transaction_service << autoscaling >> transaction_service

    # Explanation of the Diagram Components:

    # POS Device:
    # - Represents the festival attendee's point-of-sale terminal.
    # - Capable of storing transactions offline and syncing when online.

    # AWS Route 53:
    # - Manages DNS records.
    # - Routes traffic to the API Gateway.

    # API Gateway:
    # - Entry point for all API calls from POS devices.
    # - Manages traffic, security, and endpoint access.

    # Application Load Balancer (ALB):
    # - Distributes incoming traffic to the microservices.
    # - Provides scalability and high availability.

    # Microservices:
    # - Auth Service: Handles user authentication.
    # - Transaction Service: Processes transactions.
    # - User Management Service: Manages user profiles.
    # - Transaction History Service: Provides transaction history to users.

    # Databases:
    # - DynamoDB with Global Tables for multi-region replication and high availability.
    # - Aurora RDS for relational database needs.

    # Amazon S3 Bucket:
    # - Stores backups and logs.
    # - Provides durable and scalable storage.

    # AWS CloudWatch:
    # - Monitors resources and applications.
    # - Collects logs and metrics.

    # IAM and Cognito:
    # - IAM manages roles and policies for access control.
    # - Cognito provides user authentication and authorization.

    # SQS Queue:
    # - Optional component for message queuing between POS devices and Transaction Service.
    # - Helps in decoupling services and managing load.

    # CodePipeline:
    # - Represents the CI/CD pipeline for automated deployments.
    # - Ensures consistent and reliable deployment of microservices.

    # Auto Scaling:
    # - Implies that services can scale automatically based on demand.
    # - Ensures that the system can handle varying loads during festival events.

    # Edge Styles and Colors:

    # - Solid Lines: Represent active connections and data flow.
    # - Dashed Lines: Indicate asynchronous processes or backups.
    # - Dotted Lines: Represent optional or conditional connections.
    # - Edge Labels: Provide context about the connection or data transfer.
    # - Blue Edges: Secure HTTPS communications.
    # - Dark Green Edges: Backup processes to S3.
    # - Red Edges: Alerts and notifications.

    # Additional Notes:

    # - The diagram clusters components to represent the network segmentation (Public and Private Subnets).
    # - The VPC ensures secure and isolated networking within the AWS Cloud.
    # - Security best practices are implied, such as using IAM roles and policies, and encrypting data in transit and at rest.
    # - The POS Device's ability to store transactions offline ensures that attendees can make purchases without internet dependency.
    # - The use of DynamoDB Global Tables and Aurora RDS with multi-region replication ensures high availability and data consistency.
    # - CloudWatch and IAM work together to monitor the system and alert administrators of any issues.
    # - The CI/CD pipeline automates the deployment process, reducing the risk of human error and downtime.
    # - Auto Scaling ensures that the infrastructure can handle peak loads during festival events and scale down when not needed.

    # How to Run the Code on osx:

    # 0. Create virtual environment:
    # python3 -m venv venv
    # source venv/bin/activate

    # 1. Install the Diagrams Library:
    #    - Run: pip install diagrams

    # 2. Install Graphviz:
    #    - For Ubuntu/Debian: sudo apt-get install graphviz
    #    - For macOS: brew install graphviz
    #    - For Windows: Download from the official Graphviz website.

    # 3. Save this code in a file named 'festival_pos_diagram.py'.

    # 4. Run the script:
    #    - Execute: python festival_pos_diagram.py

    # 5. The script will generate an image file named 'Festival POS System Architecture.png'.

    # Customization:

    # - You can modify the components or add new ones to reflect changes in your infrastructure.
    # - The diagrams library supports many AWS services and general components for customization.

    # Additional Resources:

    # - Diagrams Documentation: https://diagrams.mingrammer.com/docs/getting-started/installation
    # - AWS Icons Reference: Use official AWS icons for accurate representations.
