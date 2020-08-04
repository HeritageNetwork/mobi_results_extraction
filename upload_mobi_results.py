import os.path
import glob
from upload_parameters import UploadParameters

# - TODO: ask user if metadata file names should be changed to gname (y/n)

# Planned process:
# 0. Validation
#    a. / excel file exists,
#       i. / tab exists, tab has egtid, gname, and cutecode
#    b. / if metadata bucket specified, it exists
#    c. / if model_prediction bucket specified, it exists
#    d. /path to model data exists
# 1. / Open excel file and generate JSON metadata from the tab (as a flat file using column headers as property keys)
# 2. / Upload JSON file to bucket as "upload_{timestamp}.json"
# 3. For each cutecode in the excel file,
#    a. / locate the %rootPath%\outputs\metadata\cutecode_{anychars}.pdf file
#    b. upload to S3 bucket with the filename (gname_without_spaces).pdf, depending on user option
#    c. / locate the %rootPath%\outputs\model_predictions\cutecode_{anychars}.tif files and upload to S3 bucket

# upload_parameters = UploadParameters()
# upload_parameters.prompt_user()
upload_parameters = UploadParameters(
    excel_file_name='UploadTestMapping.xlsx',
    excel_sheet_name='Sheet1',
    metadata_bucket='blah',
    model_prediction_bucket='blah')

excel_data_df = upload_parameters.get_excel_dataframe()
aws_helper = upload_parameters.aws_helper
metadata_bucket = upload_parameters.metadata_bucket
model_prediction_bucket = upload_parameters.model_prediction_bucket

do_live_uploads = aws_helper is not None

for row in excel_data_df.head().itertuples(index=False):
    source_root_path = os.path.join(upload_parameters.model_path, row.cutecode, 'outputs')
    if not os.path.isdir(source_root_path):
        print("{} directory was not found. Skipping...".format(source_root_path))
        continue

    if metadata_bucket is not None:
        source_file_pattern = os.path.join(source_root_path, 'metadata', "{}*.pdf".format(row.cutecode))
        for pdf_file in glob.glob(source_file_pattern):
            target_object_name = "metadata/{}".format(os.path.basename(pdf_file))
            if do_live_uploads:
                aws_helper.upload_file(metadata_bucket, target_object_name, pdf_file)

    if model_prediction_bucket is not None:
        source_file_pattern = os.path.join(source_root_path, 'model_predictions', "{}*.tif".format(row.cutecode))
        for tif_file in glob.glob(source_file_pattern):
            target_object_name = "metadata/{}".format(os.path.basename(tif_file))
            if do_live_uploads:
                aws_helper.upload_file(model_prediction_bucket, target_object_name, tif_file)

# Upload the excel data to relevant buckets
if do_live_uploads:
    json_str = excel_data_df.to_json(orient='records')
    object_name = "upload_{}.json".format(upload_parameters.time_str)
    if metadata_bucket is not None:
        aws_helper.upload_string_to_bucket(metadata_bucket, object_name, json_str)
    if model_prediction_bucket is not None:
        aws_helper.upload_string_to_bucket(model_prediction_bucket, object_name, json_str)

