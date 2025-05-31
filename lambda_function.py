import json
import boto3
from botocore.exceptions import ClientError
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image

from src.visualize import LatticeImage
from src.lattice import StateLattice
from src.knotdiagram import KnotDiagram
            
s3_client = boto3.client('s3')
            

trefoil_pd = [(6, 4, 1,3), (4, 2, 5, 1), (2, 6, 3, 5)]
link_pd = [
    (1,5,4,16),
    (16,4,15,3),
    (3,13,2,12),
    (2,11,1,12),
    (15,7,14,8),
    (8,14,9,13),
    (5,17,6,22),
    (22,6,21,7),
    (9,18,10,19),
    (19,10,20,11),
    (21,17,20,18)
]
knot_8_8 = [
    (1,7,2,6),
    (2,5,3,6),
    (5,12,4,11),
    (4,10,3,11),
    (1,8,16,7),
    (16,13,15,12),
    (13,8,14,9),
    (14,10,15,9)
]
fig_8=[
    (4,8,3,1),
    (2,7,1,6),
    (8,4,7,5),
    (6,3,5,2),
]
paper_knot = [
    (1,13,20,14),
    (19,9,18,10),
    (17,7,16,8),
    (15,1,14,2),
    (13,5,12,6),
    (11,15,10,16),
    (9,17,8,18),
    (7,3,6,4),
    (5,11,4,12),
    (3,19,2,20)
]
def main(parsed_pd_notation,fixed_segment,filename):
    diagram = KnotDiagram(parsed_pd_notation)
    lattice = StateLattice(diagram,fixed_segment)
    lattice.build_lattice()
    lattice_image = LatticeImage(lattice, image_size=(512, 1024), padding=(10, 20), text_size=9)
    lattice_image.draw_lattice(filename)
    results = {
        "number_of_states": len(lattice.nodes),
    }
    return results

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True

def parse_input(body):
    pd_notation = body.get('pd_notation', None)
    pd_notation = [tuple(crossing) for crossing in pd_notation] if pd_notation else None
    fixed_segment = body.get('fixed_segment', None)
    return (pd_notation, fixed_segment)

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    method = event['requestContext']['http']['method']
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }
    body = json.loads(event.get('body', '{}'))
    pd_notation,fixed_segment = parse_input(body)
    filename = "lattice.png"
    bucket = 'lambdaimage-testbucket'
    result = main(pd_notation, fixed_segment, '/tmp/'+filename)
    upload_file('/tmp/'+ filename , bucket ,filename)
    # Generate URL valid for 5 minutes
    s3 = boto3.client('s3')
    url = s3.generate_presigned_url('get_object', 
        Params={'Bucket': bucket, 'Key': filename},
        ExpiresIn=300
    )
    result['image_url'] = url
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': 'https://kstates.com',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(result)
    }