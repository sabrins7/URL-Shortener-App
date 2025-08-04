import json
import os
import random
import string
import boto3
from botocore.exceptions import ClientError
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
# The region will be automatically picked up from the Lambda environment
dynamodb = boto3.resource('dynamodb')
# Here I should replace 'my_DYNAMODB_TABLE_NAME' with the actual name of my DynamoDB table
# It's recommended to set this as an environment variable in Lambda.
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'short_urls') # Default to 'short_urls' if not set
table = dynamodb.Table(TABLE_NAME)

# Base URL for the shortened links (this will be the Lambda Function URL)
# This should also be set as an environment variable in Lambda.
# Example: "https://abcdefghijk.lambda-url.us-east-1.on.aws"
BASE_URL = os.environ.get('LAMBDA_FUNCTION_URL', 'https://example.com')

def generate_short_id(length=6):
    """Generates a random short ID."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def lambda_handler(event, context):
    """
    Main handler for the Lambda function.
    Handles both POST /shorten and GET /{short_id} requests.
    """
    logger.info(f"Received event: {json.dumps(event)}")

    http_method = event.get('requestContext', {}).get('http', {}).get('method')
    path = event.get('rawPath', '/')

    # Handle POST /shorten request
    if http_method == 'POST' and path == '/shorten':
        return handle_shorten_request(event)
    # Handle GET /{short_id} request
    elif http_method == 'GET' and path.startswith('/'):
        # Extract short_id from the path (e.g., /abcde -> abcde)
        short_id = path.lstrip('/')
        if short_id: # Ensure short_id is not empty after stripping '/'
            return handle_redirect_request(short_id)
        else:
            # If path is just '/', return a generic message or 404
            return {
                'statusCode': 404,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps({'message': 'Not Found. Please provide a short ID.'})
            }
    else:
        # Handle unsupported methods or paths
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'message': 'Unsupported method or path.'})
        }

def handle_shorten_request(event):
    """Handles the POST /shorten request to create a new short URL."""
    try:
        body = json.loads(event.get('body', '{}'))
        long_url = body.get('url')

        if not long_url:
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps({'message': 'Missing "url" in request body.'})
            }

        short_id = None
        max_retries = 5 # Prevent infinite loops in case of ID collisions
        for _ in range(max_retries):
            short_id = generate_short_id()
            try:
                # Try to put item only if it doesn't exist (conditional write)
                table.put_item(
                    Item={
                        'short_id': short_id,
                        'long_url': long_url
                    },
                    ConditionExpression='attribute_not_exists(short_id)'
                )
                logger.info(f"Successfully stored short_id: {short_id} for url: {long_url}")
                break # Exit loop if successful
            except ClientError as e:
                # If the short_id already exists, it will raise ConditionalCheckFailedException
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    logger.warning(f"Short ID {short_id} already exists, retrying...")
                    continue # Try generating another ID
                else:
                    raise # Re-raise other DynamoDB errors
        else:
            # This block executes if the loop finishes without a 'break'
            raise Exception("Could not generate a unique short ID after multiple retries.")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*', # Required for CORS from frontend
                'Access-Control-Allow-Methods': 'POST, GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'short_id': short_id,
                'short_url': f"{BASE_URL}/{short_id}"
            })
        }

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body.")
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'message': 'Invalid JSON in request body.'})
        }
    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'message': f'Database error: {e.response["Error"]["Message"]}'})
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }

def handle_redirect_request(short_id):
    """Handles the GET /{short_id} request to redirect to the original URL."""
    try:
        response = table.get_item(Key={'short_id': short_id})
        item = response.get('Item')

        if item and 'long_url' in item:
            long_url = item['long_url']
            logger.info(f"Redirecting short_id: {short_id} to {long_url}")
            return {
                'statusCode': 302, # HTTP 302 Found for temporary redirect
                'headers': {
                    'Location': long_url,
                    'Access-Control-Allow-Origin': '*', # Required for CORS
                    'Access-Control-Allow-Methods': 'POST, GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': '' # Body is typically empty for redirects
            }
        else:
            logger.warning(f"Short ID {short_id} not found.")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*', # Required for CORS
                    'Access-Control-Allow-Methods': 'POST, GET',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'message': 'Short URL not found.'})
            }
    except ClientError as e:
        logger.error(f"DynamoDB error during redirect: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET',
                'Access-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': f'Database error: {e.response["Error"]["Message"]}'})
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred during redirect: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET',
                'Access-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }

