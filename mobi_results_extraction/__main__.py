from .upload_mobi_results import UploadMobiResults
from .user_inputs import prompt_user


def main():
    upload_parameters = prompt_user()
    if upload_parameters is None:
        quit()
    UploadMobiResults(upload_parameters).execute()


if __name__ == '__main__':
    main()
