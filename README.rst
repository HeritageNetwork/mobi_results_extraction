MoBI Results Extraction Utility
-------------------------------
This utility is not very forgiving, so be prepared to paste the parameter data in as you are prompted.

To use, simply open a command window and do::

    # if there is any issue installing on your system, create a virtual environment to isolate the dependencies:
    python -m venv venv
    .\venv\Scripts\activate

    # install only needs to happen once, not for each execution
    python -m pip install .

    # this runs the program
    python -m mobi_results_extraction

    # if you created a virtual environment for the project, deactivate it
    .\venv\Scripts\deactivate


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


Relatively Painless Testing and Configuration
---------------------------------------------
If you don't want to answer a bunch of prompts, you can simply import the module and set it up on your own in the
python interpreter ::

    >>> from mobi_results_extraction.upload_mobi_results import UploadMobiResults
    >>> from mobi_results_extraction.upload_parameters import UploadParameters
    >>> upload_parameters = UploadParameters( \
            excel_file_name='c:\\tmp\MyTest.xlsx', \
            excel_sheet_name='Sheet1', \
            metadata_bucket='my-test-metadata-bucket', \
            model_prediction_bucket='my-test-model-predictions-bucket', \
            aws_access_key_id='my-access-key-id', \
            aws_secret_access_key='my-secret-access-key' \
        )
    >>> UploadMobiResults(upload_parameters).execute()


Alternatively, create a `__secret_run__.py` file (which is ignored by git to prevent you from accidentally checking
in your secret credentials).

.. warning::
    Creating a file like this and leaving it on the mobi server is a serious breach of security due to the
    credentials it may expose.

    Indeed, it is advisable not to leave the aws credentials visible in this file if you have it on your
    own laptop.

::

    from mobi_results_extraction.upload_mobi_results import UploadMobiResults
    from mobi_results_extraction.upload_parameters import UploadParameters


    def secret_run():
        upload_parameters = UploadParameters(
            excel_file_name='c:\\tmp\MyTest.xlsx',
            excel_sheet_name='Sheet1',
            metadata_bucket='my-test-metadata-bucket',
            model_prediction_bucket='my-test-model-predictions-bucket',
            aws_access_key_id='my-access-key-id',
            aws_secret_access_key='my-secret-access-key'
        )
        UploadMobiResults(upload_parameters).execute()

    print(__name__)
    if __name__ == '__main__':
        secret_run()


Then run it like this::

    python __secret_run__.py


