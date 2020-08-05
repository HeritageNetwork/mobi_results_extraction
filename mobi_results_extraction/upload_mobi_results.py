import os.path
import glob

# - TODO: ask user if metadata file names should be changed to gname (y/n)


class UploadMobiResults:

    def __init__(self, upload_parameters):
        self.time_str = upload_parameters.time_str
        self.model_path = upload_parameters.model_path
        self.excel_data_df = upload_parameters.get_excel_dataframe()
        self.aws_helper = upload_parameters.aws_helper
        self.metadata_bucket = upload_parameters.metadata_bucket
        self.model_prediction_bucket = upload_parameters.model_prediction_bucket

        self._do_live_uploads = self.aws_helper is not None

    def execute(self):
        for row in self.excel_data_df.head().itertuples(index=False):
            source_root_path = os.path.join(self.model_path, row.cutecode, 'outputs')
            if not os.path.isdir(source_root_path):
                print("{} directory was not found. Skipping...".format(source_root_path))
                continue

            print("\nProcessing results in {} directory...".format(source_root_path))

            if self.metadata_bucket is not None:
                source_file_pattern = os.path.join(source_root_path, 'metadata', "{}*.pdf".format(row.cutecode))
                for pdf_file in glob.glob(source_file_pattern):
                    target_object_name = "metadata/{}".format(os.path.basename(pdf_file))
                    if self._do_live_uploads:
                        print("Uploading {} to {}/{}".format(pdf_file, self.metadata_bucket, target_object_name))
                        self.aws_helper.upload_file(self.metadata_bucket, target_object_name, pdf_file)

            if self.model_prediction_bucket is not None:
                source_file_pattern = os.path.join(source_root_path, 'model_predictions', "{}*.tif".format(row.cutecode))
                for tif_file in glob.glob(source_file_pattern):
                    target_object_name = "model_predictions/{}/{}".format(row.cutecode, os.path.basename(tif_file))
                    if self._do_live_uploads:
                        print("Uploading {} to {}/{}".format(tif_file, self.model_prediction_bucket, target_object_name))
                        self.aws_helper.upload_file(self.model_prediction_bucket, target_object_name, tif_file)

        # Upload the excel data to relevant buckets
        if self._do_live_uploads:
            json_str = self.excel_data_df.to_json(orient='records')
            object_name = "upload_{}.json".format(self.time_str)
            if self.metadata_bucket is not None:
                self.aws_helper.upload_string_to_bucket(self.metadata_bucket, object_name, json_str)
            if self.model_prediction_bucket is not None:
                self.aws_helper.upload_string_to_bucket(self.model_prediction_bucket, object_name, json_str)
