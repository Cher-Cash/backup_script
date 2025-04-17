import os
import shutil


# директория с месячными бекапами и дневными бекапами тоже в константу
def show_files(path: str):
    directory_path = path
    files = os.listdir(directory_path)
    files = [f for f in files if os.path.isfile(os.path.join(directory_path, f))]
    for file in files:
        print(file)
    return files


def sort_files(file_list, rule: int):
    files = file_list
    sorted_dates = sorted(files, reverse=True)
    print("сортированные файлы:")
    for date in sorted_dates:
        print(date)
    files_for_delete = sorted_dates[rule:]
    print("files for delete: ", files_for_delete)
    return files_for_delete


def delete_old_files(file_list, directory_path):
    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            try:
                # os.remove(file_path)
                print(f"Файл {file_name} успешно удален.")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_name}: {e}")
        else:
            print(f"Файл {file_name} не найден в директории {directory_path}.")


def search_month_backups(backups_list):
    first_day_month_backups = []
    for backup in backups_list:
        if backup[8:10] == "01":
            first_day_month_backups.append(backup)
    print("бекапы месячные: ", first_day_month_backups)
    return first_day_month_backups


def move_month_backups(backups_list, directory_day, directory_month):
    backups_list_month = show_files(directory_month)
    month_set = set(backups_list_month)
    for day_backup in backups_list:
        if day_backup not in month_set:
            file_path_first_directory = os.path.join(directory_day, day_backup) # noqa: PTH118
            file_path_second_directory = os.path.join(directory_month, day_backup) # noqa: PTH118
            try:
                # Перемещаем файл в другую директорию
                shutil.move(file_path_first_directory, file_path_second_directory)
                print(f"Файл {day_backup} перемещен из {directory_day} в {directory_month}.")
            except Exception as e: # noqa: BLE001
                print(f"Ошибка при перемещении файла {day_backup}: {e}")
        else:
            print(f"Файл {day_backup} уже существует в директории {directory_month}.")




# directory - директория с файлами, rule - кол-во файлов которые выживут (сортировка по датам)
def check_backups(directory, rule:int):
    # получаем список файлов директории
    file_list = show_files(directory)
    # получаем список устаревших файлов
    old_files = sort_files(file_list, rule)
    # удаляем устаревшие файлы
    delete_old_files(old_files, directory)


def month_backups(directory_day, directory_month, rule):
    # получаем список ежедневных бекапов
    day_backups = show_files(directory_day)
    # получаем список бекапов первого числа каждого месяца
    month_backups = search_month_backups(day_backups)
    # если список не пустой переносим бекапы из директории ежедневных в директорию ежемесячных
    if month_backups:
        # в этой функции проверяем есть ли уже этот файл в дириктории ежемесячных бекапов
        move_month_backups(month_backups, directory_day, directory_month)
    # проверяем что кол-во месячных бекапов не превышает допустимое кол-во и удаляем устаревшие
    check_backups(directory_month, rule)


month_backups("/home/aleksey/backups", "/home/aleksey/backups/month",2)
check_backups("/home/aleksey/backups", 2)
