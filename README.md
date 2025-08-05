 URL Shortener Project
 This is a simple, fast, and scalable URL shortening service built on a modern serverless architecture using AWS. The project is designed for high availability and efficient redirection, offering a seamless experience for converting long URLs into compact, shareable links.

Project Status
The project is complete and ready for deployment. All required code for both the frontend and the backend Lambda functions has been fully completed and tested locally. The project is now ready to be deployed to the AWS environment to become fully active and accessible.

Key Features
Simple & Intuitive UI: A user-friendly interface for generating short links quickly.

Persistent Links: Shortened URLs are stored reliably in the database, ensuring they remain active and functional.

Efficient Redirection: The service uses a dedicated endpoint and a separate Lambda function for fast and effective redirection.

Scalable by Design: The serverless architecture on AWS Lambda and S3 ensures the application can handle high traffic volumes without performance degradation.

Technical Stack & Architecture
The project is built on a robust serverless architecture with a clear division between the frontend and backend, leveraging the following technologies:

Frontend

HTML & JavaScript: Provide the user interface and handle client-side logic.

Tailwind CSS: A utility-first CSS framework for rapid and responsive styling.

AWS S3: Hosts the static HTML and JavaScript files, serving them directly to the user.

Backend

AWS Lambda & Python: Two Python-based Lambda functions handle the core logic:

handle_shorten_request: Receives a POST request, generates a unique short_id, and stores the mapping in the database.

handle_redirect_request: Receives a GET request, retrieves the original URL from the database, and performs an HTTP redirect.

AWS DynamoDB: A NoSQL database used to store the mapping between short_id and long_url. The short_id serves as the primary key for fast lookups.

Project Structure
The project is organized in a clear, modular structure:


├── backend/                 # Contains the Python Lambda functions, Serverless config
|                              and deployment logic
|
├── frontend/                # Static files (HTML, JS, CSS) for the user interface
├── images/                  # Stores all project-related images and diagrams.
│   └── architecture_diagram.png
├── index.html               # The main entry point for the frontend.
└── README.md                    


Architecture Diagram
To gain a better understanding of the system's structure and data flow, please refer to the project's architecture diagram: (images/architecture_diagram.png)

Getting Started
These instructions will guide you through the process of deploying the project to your own AWS environment.

Prerequisites:

An active AWS account.

Python version 3.x.

Node.js & npm.

The AWS CLI configured with your credentials.

Serverless Framework installed globally.

Deployment Steps:

1. clone the Repository:
   Bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name

2. Install Project Dependencies:
   bash
   npm install

3. Deploy the Backend:
This command deploys the Lambda functions, creates the DynamoDB table, and sets up the API Gateway. Before running, you may need to set environment variables for your specific AWS region or other configurations.
   Bash
   serverless deploy


4. Upload the Frontend Files:
After deployment, you will get the API Gateway URL. Update your frontend JavaScript code with this new endpoint. Then, upload your static frontend files to the designated S3 bucket.

Bash
aws s3 sync frontend/ s3://your-s3-bucket-name --acl public-read



This project was developed with the assistance of AI tools

