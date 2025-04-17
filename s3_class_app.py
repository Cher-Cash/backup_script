import sys
from datetime import datetime

import boto3

from conf import config


class S3Api:
    def __init__(self, bucket_name, endpoint_url, aws_access_key_id, aws_secret_access_key, region_name, debug=False):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.debug = debug
        self._s3 = self.make_session()

    def make_session(self):
        session = boto3.session.Session()
        return session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )

    def move_file(self, file_name, new_file_name):
        if self.debug:
            return
        self._s3.copy_object(
            Bucket=self.bucket_name,
            CopySource={"Bucket": self.bucket_name, "Key": file_name},
            Key=new_file_name,
        )
        self._s3.delete_object(Bucket=self.bucket_name, Key=file_name)

    def delete_file(self, file):
        if self.debug:
            return
        self._s3.delete_object(Bucket=self.bucket_name, Key=file)

    def list_objects(self, need_pref):
        return self._s3.list_objects(Bucket=self.bucket_name, Prefix=need_pref)["Contents"]


def extract_datetime(filename):
    import re
    pattern = r"(\d{4}-\d{2}-\d{2})"
    match = re.search(pattern, filename)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    return None


def get_day_list(s3api, need_pref, month_pref=config["month_folder"]):
    file_list = s3api.list_objects(need_pref)
    return [
        file["Key"]
        for file in file_list
        if not file["Key"].endswith("/") and month_pref not in file["Key"]
    ]


def get_month_list(s3api, pref):
    file_list = s3api.list_objects(pref)
    return [
        file["Key"]
        for file in file_list
        if not file["Key"].endswith("/")
    ]


def search_month_backups(s3api):
    day_files = get_day_list(s3api, config["every_day_folder"])
    print(day_files)
    month_files = get_month_list(s3api, config["month_folder"])
    for file in day_files:
        date_str = extract_datetime(file)
        if date_str.day == 1:
            new_file_name = config["month_folder"] + file[8:]
            if new_file_name in month_files:
                print("file already exists")
                continue
            s3api.move_file(file, new_file_name)
            print(f"Файл перемещен: {file} -> {new_file_name}")
        continue


def sort_month_backups(s3api, param=2):
    files = get_month_list(s3api, config["month_folder"])
    valid_files = [file for file in files if extract_datetime(file) is not None]
    valid_files.sort(key=lambda x: extract_datetime(x), reverse=True)
    files_to_delete = valid_files[param:]
    for file in files_to_delete:
        s3api.delete_file(file)
        print(f"Удален файл: {file}")


def sort_everyday_backups(s3api, param=3):
    files = get_day_list(s3api, config["every_day_folder"])
    valid_files = [file for file in files if extract_datetime(file) is not None]
    valid_files.sort(key=lambda x: extract_datetime(x), reverse=True)
    print(valid_files)
    files_to_delete = valid_files[param:]
    for file in files_to_delete:
        s3api.delete_file(file)
        print(f"Удален файл: {file}")


def usage():
    print("search_month - скрипт для поиска среди ежедневных бекапов - месячный и его перенос в месячную папку\n",
          "sort_month - скрипт для сортировки чистки месячных бекапов - на вход принимает параметр int сколько свежих бекапов оставить\n",
          "sort_everyday - скрипт для сортировки чистки ежедневных бекапов - на вход принимает параметр int сколько свежих бекапов оставить\n")


commands = {"search_month":search_month_backups, "sort_month": sort_month_backups, "sort_everyday": sort_everyday_backups}


def main():
    s3api = S3Api(bucket_name=config["bucket_name"],
                  endpoint_url=config["endpoint_url"],
                  aws_access_key_id=config["aws_access_key_id"],
                  aws_secret_access_key=config["aws_secret_access_key"],
                  region_name=config["region_name"],
                  debug=True,
                  )
    if len(sys.argv) not in [2,3]:
        usage()
        sys.exit(1)
    if f := commands.get(sys.argv[1]):
        if len(sys.argv) == 3:
            return f(s3api, int(sys.argv[2]))
        return f(s3api)
    return None



if __name__ == "__main__":
    main()
