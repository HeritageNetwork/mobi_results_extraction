MoBI Results Extraction Utility
-------------------------------
This utility is not very forgiving, so be prepared to paste the parameter data in as you are prompted.

To use, simply open a command window and do::

    python -m pip install .
    python -m mobi_results_extraction


Then answer the prompts::

    Upload Model Metadata to AWS S3
    ===============================
    This program requires access to upload files to an AWS S3 bucket.
    Make sure you are prepared to supply the following:
       1. AWS Credentials to upload to S3
       2. The target AWS S3 buckets names (one for metadata, one for model data)
          (note: you can leave either blank if you are only doing upload of one type)
          (note: you can also use the same bucket for both)
       3. The name of an excel file in your working directory (current directory)
       4. The sheet name (tab) that has the cutecode mapped to egtid (and gname)
    Do you want to continue? (y/n)


Take the default location for the model results::

    Please specify the path to the model data (default: h:\spp_models)


Specify the excel file path::

    Now, supply details about the excel file that maps egtid to cutecode:
    Excel File (default is AWS_likely_spp.xlsx):
    Excel sheet name (default is AWS_sample):


Then, supply the AWS parameters::

    Please specify the AWS S3 bucket names (metadata and model_predictions).
    If you leave one blank, it will not be processed.
    Metadata S3 Bucket:
    Model Predictions S3 Bucket:

    Enter the AWS credentials for a user who has permission to upload to the buckets specified:
    AWS_ACCESS_KEY_ID:
    AWS_SECRET_ACCESS_KEY:
    AWS Region (default is us-east-1):