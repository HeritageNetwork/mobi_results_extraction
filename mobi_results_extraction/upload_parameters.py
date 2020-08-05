import time
import os.path
import pandas as pd
from aws_helper import AwsHelper
from botocore.client import ClientError


class UploadParameters:
    """
    This class manages the parameters to run the upload.
    """

    def __init__(self,
                 model_path='h:\\spp_models',
                 excel_file_name='AWS_likely_spp.xlsx',
                 excel_sheet_name='AWS_sample',
                 metadata_bucket=None,
                 model_prediction_bucket=None,
                 expected_columns=None,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_region_name='us-east-1'):
        """
        Generate the upload parameters. No parameters required required.

        Parameters
        ----------

        :param model_path: Path to the root folder where model results can be found, default 'h:\\spp_models'
        :type model_path: str
        :param excel_file_name: Path to the excel file mapping cutecode to egtid, default 'AWS_likely_spp.xlsx'
        :param excel_sheet_name: Sheet in the excel file, default 'AWS_sample'
        :param metadata_bucket: (Optional) Target bucket for metadata pdf files.
        :param model_prediction_bucket: (Optional) Target bucket for model prediction tif files.
        :param aws_access_key_id: (Optional) AWS_ACCESS_KEY_ID for the user running the script.
        :param aws_secret_access_key: (Optional) AWS_SECRET_ACCESS_KEY for the user running the script.
        :param aws_region_name: (Optional) Defaults to 'us-east-1'
        :param expected_columns: Columns to validate existence of in the spreadsheet.
            Defaults to ['cutecode', 'egtid', 'gname']
        """
        if expected_columns is None:
            expected_columns = ['cutecode', 'egtid', 'gname']
        self.model_path = model_path
        self.excel_file_name = excel_file_name
        self.excel_sheet_name = excel_sheet_name
        self.metadata_bucket = metadata_bucket
        self.model_prediction_bucket = model_prediction_bucket
        self.expected_columns = expected_columns

        self.time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
        self.__excel_data_df = None
        self.__aws_helper = None
        self.get_aws_helper(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region_name=aws_region_name)

    def get_aws_helper(self, **kwargs):
        """
        Returns the aws_helper if it has been instantiated based on the parameters supplied.

        :param `**kwargs`: (Optional) arguments to initialize AwsHelper to apply to these Upload Parameters
        :return: AwsHelper
        """
        aws_access_key_id = kwargs.pop('aws_access_key_id', None)
        aws_secret_access_key = kwargs.pop('aws_secret_access_key', None)
        aws_region_name = kwargs.pop('aws_region_name', 'us-east-1')
        if (self.__aws_helper is None) and (aws_access_key_id is not None) and (aws_secret_access_key is not None):
            self.__aws_helper = AwsHelper(aws_access_key_id, aws_secret_access_key, aws_region_name)
        return self.__aws_helper

    def get_excel_dataframe(self):
        """
        Returns the target excel spreadsheet as a DataFrame

        :return: DataFrame
        """

        if self.__excel_data_df is None:
            self.__excel_data_df = pd.read_excel(self.excel_file_name,
                                                 sheet_name=self.excel_sheet_name)
        return self.__excel_data_df

    def validate(self, aws_access_key_id, aws_secret_access_key, aws_region_name='us-east-1'):
        """
        Validates parameters.

        :param aws_access_key_id: The aws_access_key_id value to use to access AWS resources.
        :param aws_secret_access_key: The aws_secret_access_key associated with the aws_access_key_id.
        :param aws_region_name: (Optional) The aws region name. Default is 'us-east-1'
        :return: True if validation passes, else False
        """

        if self.metadata_bucket == '' and self.model_prediction_bucket == '':
            print "\n  >>  You did not specify any S3 Buckets. Exiting."
            return False

        if aws_access_key_id is None or aws_secret_access_key is None:
            print "\n  >>  You did not supply both the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. Exiting."
            return False

        aws_helper = self.get_aws_helper(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region_name=aws_region_name)
        try:
            aws_helper.validate_credentials()
        except ClientError:
            print("AWS Credentials are NOT valid.")
            return False

        if (self.metadata_bucket is not None) and (not aws_helper.bucket_exists(self.metadata_bucket)):
            return False

        if (self.model_prediction_bucket is not None) and (
                not aws_helper.bucket_exists(self.model_prediction_bucket)):
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
