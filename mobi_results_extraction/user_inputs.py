import os.path
from upload_parameters import UploadParameters


def prompt_user():
    """
    Prompts users for input and returns loaded UploadParameters, if successful.

    If not successful, returns None

    :return: UploadParameters
    """

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
    if confirm_continue.lower() != "y":
        return None

    model_path = raw_input(
        "Please specify the path to the model data (default: h:\\spp_models): ") or 'h:\\spp_models'

    print "\nNow, supply details about the excel file that maps egtid to cutecode:"
    excel_file_name = raw_input("Excel File (default is AWS_likely_spp.xlsx): ") or 'AWS_likely_spp.xlsx'
    excel_sheet_name = raw_input("Excel sheet name (default is AWS_sample): ") or 'AWS_sample'

    if not os.path.isfile(excel_file_name):
        print("{} not found. Please try again.".format(excel_file_name))
        excel_file_name = raw_input("Excel File (default is AWS_likely_spp.xlsx): ") or 'AWS_likely_spp.xlsx'

    print "\nPlease specify the AWS S3 bucket names (metadata and model_predictions)."
    print "If you leave one blank, it will not be processed."

    metadata_bucket = raw_input("Metadata S3 Bucket: ") or None
    model_prediction_bucket = raw_input("Model Predictions S3 Bucket: ") or None

    print "\nEnter the AWS credentials for a user who has permission to upload to the buckets specified:"
    aws_access_key_id = raw_input("AWS_ACCESS_KEY_ID: ") or None
    aws_secret_access_key = raw_input("AWS_SECRET_ACCESS_KEY: ") or None
    aws_region_name = raw_input("AWS Region (default is us-east-1): ") or 'us-east-1'

    upload_parameters = UploadParameters(
        model_path=model_path,
        excel_file_name=excel_file_name,
        excel_sheet_name=excel_sheet_name,
        metadata_bucket=metadata_bucket,
        model_prediction_bucket=model_prediction_bucket,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region_name=aws_region_name
    )

    if upload_parameters.validate():
        return upload_parameters
    return None
