
from boto3.session import Session
from botocore.client import ClientError


class AwsHelper:
    """
    AwsHelper contains convenience methods to access AWS resources.
    If this library gets larger, expect this helper to move to a shared location.
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region_name='us-east-1'):
        """
        Initializes an instance AwsHelper for the specified credentials.

        :param aws_access_key_id: The aws_access_key_id value to use to access AWS resources.
        :param aws_secret_access_key: The aws_secret_access_key associated with the aws_access_key_id.
        :param aws_region_name: (Optional) The aws region name. Default is 'us-east-1'
        """
        self.access_key_id = aws_access_key_id.strip()
        self.secret_access_key = aws_secret_access_key.strip()
        self.region_name = aws_region_name.strip()
        self.session = None
        self.s3_resource = None

    def __get_session(self):
        """Returns a session object, from which a resource or client can be created."""
        if self.session is None:
            self.session = Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region_name
            )
        return self.session

    def __get_s3_resource(self):
        """Returns the s3 resource."""
        if self.s3_resource is None:
            self.s3_resource = self.__get_session().resource('s3')
        return self.s3_resource

    def validate_credentials(self):
        """Validates caller identity and will raise a ClientError if invalid."""
        self.__get_session().client('sts').get_caller_identity()

    def bucket_exists(self, bucket_name):
        """Boolean. Whether a bucket exists that this user has access to view.

        :param bucket_name: Bucket to check visibility for.
        :return: True if bucket is visible to this user, else False
        """
        try:
            self.__get_session().client('s3').head_bucket(Bucket=bucket_name)
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
        s3_object = self.__get_s3_resource().Object(bucket_name, object_name)
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
        s3_object = self.__get_s3_resource().Object(bucket_name, object_name)
        try:
            s3_object.upload_file(file_path)
            return True
        except ClientError:
            print("Failed to upload file {} to bucket {}".format(file_path, bucket_name))
        return False
