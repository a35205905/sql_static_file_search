import os

SQL = ''
STATIC_FILES = []
STATIC_FOLDERS = []
DELETE_STATIC_FILES = []


def main():
    global SQL
    global STATIC_FILES
    global DELETE_STATIC_FILES

    print('-' * 20 + '開始' + '-' * 20)
    print('【一、搜索目錄設定】')
    folder_path = get_folder_path()
    print('【二、SQL 設定】')
    sql_path = get_sql_path(folder_path)
    sql_file = open(sql_path, 'r', encoding='utf-8')
    SQL = sql_file.read().replace('\n', '').replace('\r', '').strip()
    sql_file.close()
    print('【三、靜態檔案目錄設定】')
    static_file_folder_path = get_static_file_folder_path(folder_path)
    print('【四、搜索靜態檔案】')
    print('進行中...')
    search_files(static_file_folder_path)
    print('完成，已搜索到 {static_files_count} 個檔案，其中 {delete_static_files_count} 個檔案不存在於 .sql'.format(
        static_files_count=len(STATIC_FILES),
        delete_static_files_count=len(DELETE_STATIC_FILES)
    ))
    if len(DELETE_STATIC_FILES):
        is_delete = input('是否要刪除所有不存在於 .sql 的檔案？[y/n]：').lower()
        if is_delete == 'y':
            delete_files()
            delete_empty_folders()
            print('完成刪除')
        else:
            print('取消刪除')
    print('-' * 20 + '結束' + '-' * 20)


def get_folder_path():
    while True:
        path = input('請輸入欲搜索的目錄(預設為當前目錄)：')
        if path:
            if os.path.exists(path) and os.path.isdir(path):
                break
            else:
                print('"' + path + '" 目錄不存在，請重新輸入！')
        else:
            path = os.getcwd()
            break

    print('已設定目錄為 "' + path + '"')
    return path


def get_sql_path(folder_path):
    print('開始搜索 "' + folder_path + '" 中的 .sql ...')
    # 篩出該目錄底下 .sql 結尾的檔案
    files = [
        f for f in os.listdir(folder_path)
        if f.endswith('.sql') and os.path.isfile(os.path.join(folder_path, f))
    ]
    if files:
        filename = files[0]
        path = os.path.join(folder_path, files[0])
    else:
        while True:
            path = input('找不到，請自行輸入 .sql 完整路徑：')
            if os.path.exists(path) and os.path.isfile(path):
                filename = path.split('/')[-1]
                break

    print('已搜索到 ' + filename)
    return path


def get_static_file_folder_path(folder_path):
    print('開始搜索 "' + folder_path + '" 中的靜態檔案目錄(優先搜尋 S3) ...')
    # 篩出該目錄底下 s3 結尾的目錄
    folders = [
        f for f in os.listdir(folder_path)
        if f.endswith('s3') and os.path.isdir(os.path.join(folder_path, f))
    ]
    if folders:
        folder_name = folders[0]
        path = os.path.join(folder_path, folders[0])
    else:
        while True:
            path = input('找不到，請自行輸入靜態檔案目錄完整路徑：')
            if os.path.exists(path) and os.path.isdir(path):
                folder_name = path.split('/')[-1]
                break

    print('已搜索到 ' + folder_name + '/')
    return path


def search_files(folder_absolute_path, folder_relative_path='/', depth=1):
    global SQL
    global STATIC_FILES
    global STATIC_FOLDERS
    global DELETE_STATIC_FILES

    for f in os.listdir(folder_absolute_path):
        object_absolute_path = os.path.join(folder_absolute_path, f)
        # ex. project/s3/post
        if os.path.isdir(object_absolute_path):
            STATIC_FOLDERS.append(object_absolute_path)
            # 遞迴下去搜尋所有資料夾
            search_files(object_absolute_path, folder_relative_path + f + '/', depth + 1)
        # ex. project/s3/post/xxx.jpg
        elif os.path.isfile(object_absolute_path):
            # ex. /post/xxx.jpg
            object_relative_path = os.path.join(folder_relative_path, f)
            STATIC_FILES.append(object_absolute_path)
            # .sql 裡檔案路徑的開頭不會包含 / 因此判斷時要拿掉，舉例 s3://project/s3/post/xxx.jpg 在 .sql 是 post/xxx.jpg
            if object_relative_path[1:] not in SQL:
                DELETE_STATIC_FILES.append(object_absolute_path)
                print(object_relative_path + ' --> 不存在')
            else:
                print(object_relative_path)


def delete_files():
    global DELETE_STATIC_FILES

    for f in DELETE_STATIC_FILES:
        os.remove(f)
        print(f + ' ----- 已刪除')


def delete_empty_folders():
    global STATIC_FOLDERS

    for f in STATIC_FOLDERS:
        if not os.listdir(f):
            os.rmdir(f)
            print(f + '/ ----- 已刪除')


if __name__ == '__main__':
    main()
