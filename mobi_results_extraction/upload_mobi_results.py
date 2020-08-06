import os.path
import glob

# - TODO: ask user if metadata file names should be changed to gname (y/n)
# - TODO: add egt_ou_uid (requires pulling data from Biotics)
# - TODO: determine file naming for target files (e.g., tif files with cutecode in name)
# - TODO: check if user has PutObject access to buckets before doing any uploading


class UploadMobiResults:

    def __init__(self, upload_parameters):
        """
        Initializes the script to upload MoBI Results to AWS.

        :param upload_parameters: Initalized UploadParameters object
        """

        self.time_str = upload_parameters.time_str
        self.model_path = upload_parameters.model_path
        self.excel_data_df = upload_parameters.get_excel_dataframe()
        self.aws_helper = upload_parameters.get_aws_helper()
        self.metadata_bucket = upload_parameters.metadata_bucket
        self.model_prediction_bucket = upload_parameters.model_prediction_bucket
        self.aws_object_key_prefix = upload_parameters.aws_object_key_prefix

        self._do_live_uploads = self.aws_helper is not None

    def execute(self):
        """
        Runs the upload using the data in the excel spreadsheet to determine which species results to upload.

        """

        for row in self.excel_data_df.itertuples(index=False):
            source_root_path = os.path.join(self.model_path, row.cutecode, 'outputs')
            if not os.path.isdir(source_root_path):
                print("{} directory was not found. Skipping...".format(source_root_path))
                continue

            print("\nProcessing results in {} directory...".format(source_root_path))

            if self.metadata_bucket is not None:
                source_file_pattern = os.path.join(source_root_path, 'metadata', "{}*.pdf".format(row.cutecode))
                for pdf_file in glob.glob(source_file_pattern):
                    target_object_name = "{}metadata/{}".format(self.aws_object_key_prefix, os.path.basename(pdf_file))
                    if self._do_live_uploads:
                        print("Uploading {} to {}/{}".format(pdf_file, self.metadata_bucket, target_object_name))
                        self.aws_helper.upload_file(self.metadata_bucket, target_object_name, pdf_file)

            if self.model_prediction_bucket is not None:
                source_file_pattern = os.path.join(source_root_path, 'model_predictions', "{}*.tif".format(row.cutecode))
                for tif_file in glob.glob(source_file_pattern):
                    target_object_name = "{}model_predictions/{}/{}".format(self.aws_object_key_prefix, row.cutecode, os.path.basename(tif_file))
                    if self._do_live_uploads:
                        print("Uploading {} to {}/{}".format(tif_file, self.model_prediction_bucket, target_object_name))
                        self.aws_helper.upload_file(self.model_prediction_bucket, target_object_name, tif_file)

                # handle aquatic
                source_file_pattern = os.path.join(source_root_path, 'model_predictions', "{}*_threshold_MoBI_*.*".format(row.cutecode))
                for shp_file_part in glob.glob(source_file_pattern):
                    target_object_name = "{}model_predictions/{}/{}".format(self.aws_object_key_prefix, row.cutecode, os.path.basename(shp_file_part))
                    if self._do_live_uploads:
                        print("Uploading {} to {}/{}".format(shp_file_part, self.model_prediction_bucket, target_object_name))
                        self.aws_helper.upload_file(self.model_prediction_bucket, target_object_name, shp_file_part)

        # Upload the excel data to relevant buckets
        if self._do_live_uploads:
            json_str = self.excel_data_df.to_json(orient='records')
            object_name = "upload_{}.json".format(self.time_str)
            if self.metadata_bucket is not None:
                self.aws_helper.upload_string_to_bucket(self.metadata_bucket, object_name, json_str)
            if self.model_prediction_bucket is not None:
                self.aws_helper.upload_string_to_bucket(self.model_prediction_bucket, object_name, json_str)
