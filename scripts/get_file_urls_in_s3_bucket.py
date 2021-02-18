####################################
#   File name: get_file_urls_in_s3_bucket.py
#   About: Process for obtainng the urls for all files in a amazon s3 bucket
#   Author: Geoff Taylor | Imagery & Remote Sensing Team | Esri
#   Date created: 01/21/2021
#   Date last modified: 01/26/2021
#   Python Version: 3.7
####################################

import pandas as pd
from arcpy import AddError, CheckExtension, CheckOutExtension, CheckInExtension
# Ensure Amazon AWS boto3 is installed
try:
    from boto3 import client, resource
except ModuleNotFoundError:
    AddError("boto3 required to run process. Detected Boto3 missing.")
    AddError("install boto3 using conda")
    AddError("conda install -c anaconda boto3")
    AddError("learn more on Boto3 https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration")
    print("boto3 required to run process. Detected Boto3 missing.")
    print("install boto3 using conda")
    print("conda install -c anaconda boto3")
    print("learn more on Boto3 https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration")



def make_boolean(in_value):
    # Ensure list folders text-based boolean input is converted to boolean
    if in_value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh']:
        return True
    else:
        return False


def process():
    # TODO: Add User Error Reporting alerting user of issue with accessing their bucket.
    # Begin Script
    class LicenseError(Exception):
        pass

    try:
        if CheckExtension("ImageAnalyst") == "Available":
            CheckOutExtension("ImageAnalyst")
        else:
            # raise a custom exception
            raise LicenseError
        try:
            bucket_url = 'https://s3.{0}.amazonaws.com/{1}/'.format(region, bucket_name)
            f_list = []
            fp_list = []
            '''
            conn = client('s3')  # again assumes boto.cfg setup, assume AWS S3
            
            for key in conn.list_objects(Bucket=bucket_name)['Contents']:
                if not key['Key'].endswith('/') and list_folders is False:
                    f_list.append(key['Key'])
                    fp_list.append(bucket_url + key['Key'])
                if list_folders is True:
                    f_list.append(key['Key'])
                    fp_list.append(bucket_url + key['Key'])
            '''
            s3r = resource('s3')
            bucket_list = [item.key for item in list(s3r.Bucket(bucket_name).objects.all())]
            for key in bucket_list:
                if not key.endswith('/') and list_folders is False:
                    f_list.append(key)
                    fp_list.append(bucket_url + key)
                if list_folders is True:
                    f_list.append(key)
                    fp_list.append(bucket_url + key)


            # Create a Pandas dataframe from the data.
            df = pd.DataFrame({'bucket_url': bucket_url, 'key': f_list, 'full_path': fp_list})

            with pd.ExcelWriter(out_spreadsheet) as writer:
                df.to_excel(writer)
        except NoCredentialsError:
            err_str = 'Detected Boto3 Credentials are not set. see the following instructions ' \
                      'https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration'
            AddError(err_str)
            raiseValueError(err_str)
        except s3_client.exceptions.NoSuchBucket:
            AddError('Aws bucket %s does not exist' % bucket_name)
            raise ValueError('Aws bucket %s does not exist' % bucket_name)
        # Check back in Image Analyst license
        CheckInExtension("ImageAnalyst")
    except LicenseError:
        AddError("ImageAnalyst license is unavailable")
        print("ImageAnalyst license is unavailable")
    except ExecuteError:
        AddError(GetMessages(2))
        print(GetMessages(2))


if __name__ == "__main__":
    debug = False
    if debug:
        ''''''
        # User Input Variables
        bucket_name = 'pge-mosaicimagery'
        region = 'us-east-1'
        out_spreadsheet = r'C:\Users\geof7015\Documents\GitHub\esri_lidar_3d_management\test\s3_bucket_files3.xlsx'
        list_folders = False
    else:
        from arcpy import GetParameterAsText
        # User Input Variables
        bucket_name = GetParameterAsText(0)
        region = GetParameterAsText(1)
        out_spreadsheet = GetParameterAsText(2)
        list_folders = make_boolean(GetParameterAsText(3))
    process()
