import pyzipper
import os



def uncompress(zip_file_path, password):
    password_bytes = password.encode('utf-8')
    unzip_file_name = zip_file_path.split(os.sep)[-1].split(".zip")[0]
    zip_folder_path = os.path.abspath(os.path.join(zip_file_path, os.pardir))
    with pyzipper.AESZipFile(zip_file_path) as zf:
        zf.extractall(path=zip_folder_path, pwd=password_bytes)


    unzip_file_path = os.path.join(zip_folder_path, unzip_file_name)

    return unzip_file_path


def delete_unzipped_file(unzip_file_path):
    # os.remove(unzip_file_path)
    return


if __name__ == "__main__":
    zip_file_path = r"G:\preprocessed_cluster\intermediate_file\sharpnessnextpouch@timestudy_com\2021-01-01\phone_GPS_clean_2021-01-01.csv.zip"

    password = "TIMEisthenewMICROTStudy-NUUSC"
    unzip_file_path = uncompress(zip_file_path, password)

    # delete_unzipped_file(unzip_file_path)
