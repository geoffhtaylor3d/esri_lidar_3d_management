####################################
#   File name: get_file_urls_in_s3_bucket.py
#   About: Process for obtainng the urls for all files in a amazon s3 bucket
#   Author: Geoff Taylor | Imagery & Remote Sensing Team | Esri
#   Date created: 01/21/2021
#   Date last modified: 01/21/2021
#   Python Version: 3.7
####################################

import pandas as pd
# Ensure Amazon AWS boto3 is installed
try:
    from boto3 import client
except ModuleNotFoundError:
    print("boto3 required to run process. Detected Boto3 missing.")
    print("install boto3 using conda")
    print("conda install -c anaconda boto3")


def process():
    # Begin Script
    bucket_url = 'https://s3.{0}.amazonaws.com/{1}/'.format(region, bucket_name)
    conn = client('s3')  # again assumes boto.cfg setup, assume AWS S3
    f_list = []
    fp_list = []
    for key in conn.list_objects(Bucket=bucket_name)['Contents']:
        if not key['Key'].endswith('/') and list_folders is False:
            f_list.append(key['Key'])
            fp_list.append(bucket_url + key['Key'])
        if list_folders is True:
            f_list.append(key['Key'])
            fp_list.append(bucket_url + key['Key'])

    # Create a Pandas dataframe from the data.
    df = pd.DataFrame({'bucket_url': bucket_url, 'key': f_list, 'full_path': fp_list})

    with pd.ExcelWriter(out_spreadsheet) as writer:
        df.to_excel(writer)


if "name" == "__main__":
    debug = False
    if debug:
        # User Input Variables
        bucket_name = 'esri-imagery-demo-data'
        region = 'us-east-1'
        out_spreadsheet = 's3_bucket_files3.xlsx'
        list_folders = False
    else:
        from arcpy import GetParameterAsText
        # User Input Variables
        bucket_name = GetParameterAsText(0)
        region = GetParameterAsText(1)
        out_spreadsheet = GetParameterAsText(2)
        list_folders = GetParameterAsText(3)
