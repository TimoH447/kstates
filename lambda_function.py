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
from src.two_bridge_knots import TwoBridgeKnot
            
def compute_lattice_data(parsed_pd_notation,fixed_segment,filename=None):
    """
    Compute the state lattice for a given knot diagram and fixed segment, and generate an image of the lattice.
    """
    diagram = KnotDiagram(parsed_pd_notation)
    lattice = StateLattice(diagram,fixed_segment)
    if filename:
        lattice_image = LatticeImage(lattice, image_size=(512, 1024), padding=(10, 20), text_size=9)
        lattice_image.draw_lattice(filename)
    results = {
        "number_of_states": len(lattice.nodes),
        "f_polynomial": lattice.get_f_polynomial_latex(),
        "alexander_polynomial": lattice.get_alexander_polynomial_latex(),
        "minimal_state": str(lattice.get_minimal_state()),
        "maximal_state": str(lattice.get_maximal_state()),
        "sequence_min_to_max": str(lattice.get_sequence_min_to_max()),
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

def parse_pd_input(body):
    pd_notation = body.get('knot_input', None)
    pd_notation = [tuple(crossing) for crossing in pd_notation] if pd_notation else None
    fixed_segment = body.get('fixed_segment', None)
    return (pd_notation, fixed_segment)

def parse_tb_input(body):
    tb_notation = body.get('knot_input')
    tb_notation = tb_notation.split(",")
    tb_notation = list(map(int,tb_notation))
    tb_knot = TwoBridgeKnot(tb_notation)
    pd_notation = tb_knot.get_pd_notation()
    fixed_segment = body.get('fixed_segment', None)
    return pd_notation,fixed_segment


def parse_input(body):
    notation_type = body.get('notation_type','pd')
    if notation_type == 'tb':
        pd_notation, fixed_segment = parse_tb_input(body)
    else:
        pd_notation,fixed_segment = parse_pd_input(body)
    return pd_notation,fixed_segment 

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    """
    bucket = 'lambdaimage-testbucket'
    filename = "lattice.png"

    #### Handle CORS preflight request
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

    #### Handle POST request
    # parsing the body of the event
    body = json.loads(event.get('body', '{}'))
    pd_notation,fixed_segment = parse_input(body)
    number_of_crossings = len(pd_notation) if pd_notation else 0
    
    if number_of_crossings > 20:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Too many crossings. Please provide a knot with 20 or fewer crossings.'
            }),
        }

    # calculate the lattice and generate the image 
    if number_of_crossings > 11:
        result = compute_lattice_data(pd_notation, fixed_segment)
    else:
        result = compute_lattice_data(pd_notation, fixed_segment,'/tmp/'+ filename)

        #upload lattice image to S3
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
        'body': json.dumps(result)
    }