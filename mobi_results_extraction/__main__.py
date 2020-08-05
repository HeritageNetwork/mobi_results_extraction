from upload_mobi_results import UploadMobiResults
from upload_parameters import UploadParameters


def main():
    upload_parameters = UploadParameters()
    if not upload_parameters.prompt_user():
        quit()
    UploadMobiResults(upload_parameters).execute()


if __name__ == '__main__':
    main()
