from upload_mobi_results import UploadMobiResults
import user_inputs


def main():
    upload_parameters = user_inputs.prompt_user()
    if upload_parameters is None:
        quit()
    UploadMobiResults(upload_parameters).execute()


if __name__ == '__main__':
    main()
