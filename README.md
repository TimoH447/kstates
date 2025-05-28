# kstates - Kauffman states of knot diagrams
This project computes the Kauffman state lattice of a knot diagram which is 
given in planar diagram (PD) notation.

## Background
Kauffman states of a knot diagram are given by assigning a marker at each crossing in one of the four incident regions and which satisfy that no region contains more than one marker.
If two markers are adjacent to the same segment we can swap the region of the markers at the crossing to obtain a new Kauffman state. This is called state transposition.
Kauffman showed that the Kauffman states together with the state transposition form a lattice.

To calculate the Kauffman states of a knot diagram, the knot diagram has to be inserted 
in planar diagram (PD) notation. The notation is explained [here](https://knotinfo.math.indiana.edu/descriptions/pd_notation.html).

## Backend
We want an API that our front end can call and returns the image of the Kauffman lattice and some futher information. Instead of renting the complete infrastructure we use FaaS (Function as a Service) which is offered by AWS Lambda. To access the function from outside we use Amazon API Gateway.
1. Create Lambda Function:

    To use the Pillow and Boto3 package in Aws Lambda, add the packages to this folder with the command:
    pip install --platform manylinux2014_x86_64 --target=dir_name --implementation cp --python-version 3.13 --only-binary=:all: --upgrade Pillow boto3 
    And add permissions to the lambda function to write to S3

    We keep the bucket with the lattice images private and return instead pre signed links with which one can access a specific image for 5 minutes.

    To access the API later from our front end on a different domain, the lambda function has to return the required CORS (cross-origin-resource-sharing) headears:
    ```
    import json
    def lambda_handler(event, context):
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': 'https://www.example.com',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps('Hello from Lambda!')
    }```
    
2. AWS Gateway:


Invoking Lambda function:    https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html 

## Frontend
1. S3 bucket
2. Cloudfront

