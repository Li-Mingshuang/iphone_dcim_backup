from win32com.shell import shell, shellcon
from win32com.propsys import propsys
from datetime import datetime
import pythoncom
import os
import time
import argparse

# squanchy221218
import json
from tqdm import tqdm

INTERESTING_EXTENSIONS = [".jpg", ".mov", ".heic", ".mp4"]
DATE_PROP_KEY = propsys.PSGetPropertyKeyFromName("System.DateModified")
DATE_ARG_PARSE_STR = '%Y-%m-%d'
DATE_PROP_PARSE_STR = '%Y/%m/%d:%H:%M:%S.%f' # not sure bout the f modifier but it does not really matter
older_than_datetime = None


# 此处设置Iphone DCIM路径、备份目标路径以及log保存路径（默认为代码文件所在路径）
log_pth = r'.'
input_path = r'此电脑\Apple iPhone\Internal Storage\DCIM'
output_path = r'E:\myFiles\backup\221218_iphone'


def recurse_and_get_ishellfolder(base_ishellfolder, path):
    splitted_path = path.split("\\", 1)

    for pidl in base_ishellfolder:
        if base_ishellfolder.GetDisplayNameOf(pidl, shellcon.SHGDN_NORMAL) == splitted_path[0]:
            break

    folder = base_ishellfolder.BindToObject(pidl, None, shell.IID_IShellFolder)

    if len(splitted_path) > 1:
        # More to recurse
        return recurse_and_get_ishellfolder(folder, splitted_path[1])
    else:
        return folder


def move_files(args):
    main_folder = recurse_and_get_ishellfolder(shell.SHGetDesktopFolder(), args.input)

    for photo_folder_pidl in tqdm(main_folder):
        folder_name = main_folder.GetDisplayNameOf(photo_folder_pidl, shellcon.SHGDN_NORMAL)
        # print(folder_name)
        folder = main_folder.BindToObject(photo_folder_pidl, None, shell.IID_IShellFolder)
        for pidl in folder:
            child_name = folder.GetDisplayNameOf(pidl, shellcon.SHGDN_NORMAL)
            ext_lower = os.path.splitext(child_name)[1].lower()

            # squanchy221218
            # print(ext_lower)
            #
            # if ext_lower in INTERESTING_EXTENSIONS:
            # if not ext_lower == '.mov':
            file_mod_date = getmodified_datetime_by_pidl(folder, pidl)
            if not older_than_datetime or file_mod_date < older_than_datetime:
                filename = folder_name[:-2] + "_" + child_name
                # print(folder_name)
                # print(folder_name[:-2])

                if filename not in success_files:
                    print("Transferring file: " + child_name)
                    # 去掉文件夹 年月 后的后缀
                    # move_file_by_pidl(args.output, folder, pidl, child_name, folder_name + "_")
                    move_file_by_pidl(args.output, folder, pidl, child_name, folder_name[:-2] + "_")
                else:
                    # print(f'{filename} exist!')
                    pass

            else:
                print("Skipping too recent file: " + child_name)


def move_file_by_pidl(dest_dir, src_ishellfolder, src_pidl, src_filename, name_prefix):
    filename = name_prefix + src_filename  # Avoid conflicts
    dest_fullpath = dest_dir + os.sep + filename
    tries = 2
    i = 1
    while True:
        # print(filename)

        # if filename in success_files:
        #     print(f'{filename} exist!')
        #     break

        res = move_file_by_pidl_to_path(src_ishellfolder, src_pidl, dest_dir, filename)
        if res:
            if not os.path.isfile(dest_fullpath):
                print(" -> Move operation returned ok but file did not appear")

                fail_files.append(filename)
                with open(fail_log_file, 'w') as f:
                    json.dump(fail_files, f)
            else:
                success_files.append(filename)
                with open(success_log_file, 'w') as f:
                    json.dump(success_files, f)

            break

        if i < tries:
            i += 1
            time.sleep(3)
        else:
            print(" -> Failed to transfer " + src_filename)

            fail_files.append(filename)
            with open(fail_log_file, 'w') as f:
                json.dump(fail_files, f)

            break


def getmodified_datetime_by_pidl(src_ishellfolder, src_pidl):
    fidl = shell.SHGetIDListFromObject(src_ishellfolder)  # Grab the PIDL from the folder object
    si = shell.SHCreateShellItem(fidl, None, src_pidl)  # Create a ShellItem of the source file
    ps = propsys.PSGetItemPropertyHandler(si)
    date_str = ps.GetValue(DATE_PROP_KEY).ToString()
    return datetime.strptime(date_str, DATE_PROP_PARSE_STR)


def move_file_by_pidl_to_path(src_ishellfolder, src_pidl, dst_path, dst_filename):
    pidl_folder_dst, flags = shell.SHILCreateFromPath(dst_path, 0)
    dst_ishellfolder = shell.SHGetDesktopFolder().BindToObject(pidl_folder_dst, None, shell.IID_IShellFolder)

    fidl = shell.SHGetIDListFromObject(src_ishellfolder)  # Grab the PIDL from the folder object
    didl = shell.SHGetIDListFromObject(dst_ishellfolder)  # Grab the PIDL from the folder object

    si = shell.SHCreateShellItem(fidl, None, src_pidl)  # Create a ShellItem of the source file
    dst = shell.SHCreateItemFromIDList(didl)

    pfo = pythoncom.CoCreateInstance(shell.CLSID_FileOperation, None, pythoncom.CLSCTX_ALL, shell.IID_IFileOperation)
    pfo.SetOperationFlags(shellcon.FOF_NOCONFIRMATION | shellcon.FOF_SILENT | shellcon.FOF_NOERRORUI)

    # squanchy221218: 改移动为复制
    # pfo.MoveItem(si, dst, dst_filename) # Schedule an operation to be performed
    # pfo.CopyItem(si, dst, "Destination Name.jpg")
    pfo.CopyItem(si, dst, dst_filename)
    pfo.PerformOperations()

    return not pfo.GetAnyOperationsAborted()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--older-than", help="Only move photos older than YYYY-MM-DD")
    parser.add_argument("-i", "--input", default=input_path, help="input path, e.g. \"This PC\Apple iPhone\Internal Storage\DCIM\"")
    parser.add_argument("-o", "--output", default=output_path, help="output directory, must exist")
    args = parser.parse_args()

    if not args.input:
        print("You must specify input path pointing to iPhone photos")
        exit(-1)
    else:
        print(args.input)
    if not args.output:
        print("You must specify output path")
        exit(-1)
    else:
        print(args.output)
    if not os.path.isdir(args.output):
        print("Output path does not exist: " + args.output)
        exit(-1)
    if args.older_than:
        print("Only moving files older than " + args.older_than)
        older_than_datetime = datetime.strptime(args.older_than, DATE_ARG_PARSE_STR)


    fail_files = []
    success_files = []
    # log_pth = r'E:\myFiles\backup'

    fail_log_file = os.path.join(log_pth, 'fail_log.json')
    success_log_file = os.path.join(log_pth, 'success_log.json')

    if os.path.isfile(success_log_file):
        with open(success_log_file) as f:
            success_files = json.load(f)
            print(f'读取success log成功，已复制成功文件数：{len(success_files)}')

    while True:
        try:
            move_files(args)
        except:
            time.sleep(10)
            print('waiting for reconnecting')

    print('file failed to copy:')
    for file in fail_files:
        print(file)





