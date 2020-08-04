import time
import os.path
import pandas
from botocore.client import ClientError
from boto3.session import Session

# Expectations:
# / ask user for AWS credentials
# / ask user for bucket path for metadata (must exist, and user must have permissions to upload to it)
# / ask user for bucket path for model_predictions (if empty, no model_predictions will be transferred)
# / ask user for excel filename (that has egtid,gname,cutecode mapping)
# / ask user for tab name in the excel file
# / ask user for the root path to operate on (e.g. h:\spp_models)
# - TODO: ask user if metadata file names should be changed to gname (y/n)

# Planned process:
# 0. Validation
#    a. excel file exists, tab exists, tab has egtid, gname, and cutecode
#    b. / if metadata bucket specified, it exists
#    c. / if model_prediction bucket specified, it exists
#    d. path to model data exists
# 1. / Open excel file and generate JSON metadata from the tab (as a flat file using column headers as property keys)
# 2. Upload JSON file to bucket as "upload_{timestamp}.json"
# 3. For each cutecode in the excel file,
#    a. locate the %rootPath%\outputs\metadata\cutecode_{anychars}.pdf file
#    b. upload to S3 bucket with the filename (gname_without_spaces).pdf, depending on user option
#    c. locate the %rootPath%\outputs\model_predictions\cutecode_{anychars}.tif files and upload to S3 bucket, depending on user option

print "\nUpload Model Metadata to AWS S3"
print "==============================="
print "This program requires access to upload files to an AWS S3 bucket."
print "Make sure you are prepared to supply the following:"
print "   1. AWS Credentials to upload to S3"
print "   2. The target AWS S3 buckets names (one for metadata, one for model data)"
print "      (note: you can leave either blank if you are only doing upload of one type)"
print "      (note: you can also use the same bucket for both)"
print "   3. The name of an excel file in your working directory (current directory)"
print "   4. The sheet name (tab) that has the cutecode mapped to egtid (and gname)"
confirm_continue = raw_input("Do you want to continue? (y/n)") or "n"
if confirm_continue.lower() == "n":
    quit()

model_path = raw_input("Please specify the path to the model data (default: h:\\spp_models): ") or "h:\\spp_models"

print "\nPlease specify the AWS S3 bucket names (metadata and model_predictions)."
print "If you leave one blank, it will not be processed."

aws_region_name = raw_input("AWS Region (default is us-east-1): ") or "us-east-1"
metadata_bucket = raw_input("Metadata S3 Bucket: ")
model_prediction_bucket = raw_input("Model Preditions S3 Bucket: ")
if metadata_bucket == '' and model_prediction_bucket == '':
    print "\n  >>  You did not specify any S3 Buckets. Exiting."
    quit()

print "\nEnter the AWS credentials for a user who has permission to upload to the buckets specified:"
aws_access_key_id = raw_input("AWS_ACCESS_KEY_ID: ")
aws_secret_access_key = raw_input("AWS_SECRET_ACCESS_KEY: ")
if aws_access_key_id == '' or aws_secret_access_key == '':
    print "\n  >>  You did not supply both the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. Exiting."
    quit()

s3_session = Session(
    aws_access_key_id=aws_access_key_id.strip(),
    aws_secret_access_key=aws_secret_access_key.strip(),
    region_name=aws_region_name.strip()
)

s3 = s3_session.resource('s3')

try:
    s3.get_caller_identity()
except ClientError:
    print("AWS Credentials are NOT valid.")
    quit()

# TODO: get rid of this code duplication
if metadata_bucket != '':
    try:
        s3.head_bucket(Bucket=metadata_bucket)
    except ClientError:
        print("{} bucket not found".format(metadata_bucket))
        quit()

if model_prediction_bucket != '':
    try:
        s3.head_bucket(Bucket=model_prediction_bucket)
    except ClientError:
        print("{} bucket not found".format(model_prediction_bucket))
        quit()

print "\nNow, supply details about the excel file that maps egtid to cutecode:"
excel_file_name = raw_input("Excel File (default is AWS_likely_spp.xlsx): ") or "AWS_likely_spp.xlsx"
excel_sheet_name = raw_input("Excel sheet name (default is AWS_sample): ") or "AWS_sample"

if not os.path.isfile(excel_file_name):
    print("{} not found".format(excel_file_name))
    quit()

excel_data_df = pandas.read_excel(excel_file_name, sheet_name=excel_sheet_name)
json_str = excel_data_df.to_json(orient='records')
time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
if metadata_bucket != '':
    s3_object = s3.Object(metadata_bucket, "metadata/upload_{}.json".format(time_str))
    s3_object.put(Body=json_str)

