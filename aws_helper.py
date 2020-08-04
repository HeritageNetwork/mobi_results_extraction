
from boto3.session import Session
from botocore.client import ClientError


class AwsHelper:
    def __init__(self, access_key_id, secret_access_key, region_name):
        self.access_key_id = access_key_id.strip()
        self.secret_access_key = secret_access_key.strip()
        self.region_name = region_name.strip()
        self.session = None
        self.s3_resource = None

    def get_session(self):
        """Returns a session object, from which a resource or client can be created."""
        if self.session is None:
            self.session = Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region_name
            )
        return self.session

    def get_s3_resource(self):
        """Returns the s3 resource."""
        if self.s3_resource is None:
            self.s3_resource = self.get_session().resource('s3')
        return self.s3_resource

    def validate_credentials_for_s3(self):
        """Validates caller identity and will raise a ClientError if invalid."""
        self.get_s3_resource().get_caller_identity()

    def bucket_exists(self, bucket_name):
        """Boolean. Whether a bucket exists that this user has access to view."""
        try:
            self.get_s3_resource().head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            print("{} bucket not found".format(bucket_name))
        return False

    def upload_string_to_bucket(self, bucket_name, object_name, body_content):
        """Convenience method to upload a string (e.g., JSON string) as a file to S3.

        :param bucket_name: Bucket to upload to
        :param object_name: S3 object name
        :param body_content: String to save as object
        :return: True if file was uploaded, else False
        """
        s3_object = self.get_s3_resource().Object(bucket_name, object_name)
        try:
            s3_object.put(Body=body_content)
            return True
        except ClientError:
            print("Failed to upload string to bucket {}".format(bucket_name))
        return False

    def upload_file(self, bucket_name, object_name, file_path):
        """Upload a file to an S3 bucket

        :param bucket_name: Bucket to upload to
        :param object_name: S3 object name.
        :param file_path: File to upload
        :return: True if file was uploaded, else False
        """
        s3_object = self.get_s3_resource().Object(bucket_name, object_name)
        try:
            s3_object.upload_file(file_path)
            return True
        except ClientError:
            print("Failed to upload file {} to bucket {}".format(file_path, bucket_name))
        return False
