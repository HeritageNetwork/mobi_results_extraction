import time
import os.path
import pandas as pd
from aws_helper import AwsHelper
from botocore.client import ClientError


class UploadParameters:

    def __init__(self, **kwargs):
        self.model_path = kwargs.get('model_path', 'h:\\spp_models')
        self.excel_file_name = kwargs.get('excel_file_name', 'AWS_likely_spp.xlsx')
        self.excel_sheet_name = kwargs.get('excel_sheet_name', 'AWS_sample')
        self.expected_columns = kwargs.get('expected_columns', ['cutecode', 'egtid', 'gname'])
        self.metadata_bucket = kwargs.get('metadata_bucket', None)
        self.model_prediction_bucket = kwargs.get('model_prediction_bucket', None)

        self.time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.aws_helper = None
        self.excel_data_df = None

    def get_excel_dataframe(self):
        if self.excel_data_df is None:
            self.excel_data_df = pd.read_excel(self.excel_file_name,
                                               sheet_name=self.excel_sheet_name)
        return self.excel_data_df

    def validate(self, aws_access_key_id, aws_secret_access_key, aws_region_name):

        if self.metadata_bucket == '' and self.model_prediction_bucket == '':
            print "\n  >>  You did not specify any S3 Buckets. Exiting."
            return False

        if aws_access_key_id is None or aws_secret_access_key is None:
            print "\n  >>  You did not supply both the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. Exiting."
            return False

        self.aws_helper = AwsHelper(aws_access_key_id, aws_secret_access_key, aws_region_name)
        try:
            self.aws_helper.validate_credentials_for_s3()
        except ClientError:
            print("AWS Credentials are NOT valid.")
            return False

        if (self.metadata_bucket is not None) and (not self.aws_helper.bucket_exists(self.metadata_bucket)):
            return False

        if (self.model_prediction_bucket is not None) and (
                not self.aws_helper.bucket_exists(self.model_prediction_bucket)):
            return False

        if not os.path.isdir(self.model_path):
            print("{} does not appear to be a valid directory".format(self.model_path))
            return False

        if not os.path.isfile(self.excel_file_name):
            print("{} not found".format(self.excel_file_name))
            return False

        if not all(elem in self.get_excel_dataframe().columns.values for elem in self.expected_columns):
            print("{} did not contain expected columns: {}".format(self.excel_file_name, self.expected_columns))
            return False

        return True

    def prompt_user(self):
        """Boolean if successful. Prompts user for inputs and stops in the event of a validation failure."""

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
            return False

        self.model_path = raw_input(
            "Please specify the path to the model data (default: h:\\spp_models): ") or 'h:\\spp_models'

        print "\nPlease specify the AWS S3 bucket names (metadata and model_predictions)."
        print "If you leave one blank, it will not be processed."

        self.metadata_bucket = raw_input("Metadata S3 Bucket: ") or None
        self.model_prediction_bucket = raw_input("Model Preditions S3 Bucket: ") or None

        print "\nEnter the AWS credentials for a user who has permission to upload to the buckets specified:"
        aws_access_key_id = raw_input("AWS_ACCESS_KEY_ID: ") or None
        aws_secret_access_key = raw_input("AWS_SECRET_ACCESS_KEY: ") or None
        aws_region_name = raw_input("AWS Region (default is us-east-1): ") or 'us-east-1'

        print "\nNow, supply details about the excel file that maps egtid to cutecode:"
        self.excel_file_name = raw_input("Excel File (default is AWS_likely_spp.xlsx): ") or 'AWS_likely_spp.xlsx'
        self.excel_sheet_name = raw_input("Excel sheet name (default is AWS_sample): ") or 'AWS_sample'

        return self.validate(aws_access_key_id, aws_secret_access_key, aws_region_name)
