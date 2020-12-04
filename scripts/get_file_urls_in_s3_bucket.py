from boto3 import client
import pandas as pd

# User Input Variables
bucket_name = 'esri-imagery-demo-data'
region = 'us-east-1'
out_spreadsheet = 's3_bucket_files3.xlsx'
list_folders = False

# Begin Sctipt
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

