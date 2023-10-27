import os
import shutil
import re
from tqdm import tqdm

root = r'E:\myFiles\backup\221218\2023'
output_pth = r'E:\myFiles\backup\221218\2023'

folders = os.listdir(root)

# for folder in folders:
# folder_pth = os.path.join(root, folder)

def collect_photo_mov(folder_pth, output_pth=None):
    """
    lms230429:
    folder_pth为需要提取照片mov文件的路径
    output_pth=None时，收集到的照片mov文件保存在当前目录下的新建文件夹中，否则位于output_pth的新建文件夹
    新建文件夹名为”MOV_当前目录最后一级文件夹名”
    """
    files = os.listdir(folder_pth)

    file_name_cnt = {}

    # for file in tqdm(files):
    for file in files:
        file_pth = os.path.join(folder_pth, file)

        if not os.path.isfile(file_pth):
            continue

        file_name, ext = os.path.splitext(file)

        if ext.lower() not in ['.mov', '.heic', 'png', 'jpg']:
            continue

        if file_name not in file_name_cnt:
            file_name_cnt[file_name] = 1
        else:
            file_name_cnt[file_name] += 1

    # print(file_name_cnt)

    mov_cnt = 0

    # tar_folder = os.path.join(folder_pth, 'MOV_' + folder_pth.split('\\')[-1])
    # if not os.path.exists(tar_folder):
    #     os.makedirs(tar_folder)

    tar_folder_pth = None

    for file in tqdm(files):
        file_pth = os.path.join(folder_pth, file)

        if not os.path.isfile(file_pth):
            continue

        file_name, ext = os.path.splitext(file)

        if ext.lower() != '.mov':
            continue

        if file_name_cnt[file_name] != 2:
            continue

        tar_folder_name = 'MOV_' + folder_pth.split('\\')[-1]

        if output_pth:
            tar_folder_pth = os.path.join(output_pth, tar_folder_name)
        else:
            tar_folder_pth = os.path.join(folder_pth, tar_folder_name)

        if not os.path.exists(tar_folder_pth):
            os.makedirs(tar_folder_pth)

        tar_pth = os.path.join(tar_folder_pth, file)
        shutil.move(file_pth, tar_pth)

        print(tar_pth)

        mov_cnt += 1

    print()
    if not tar_folder_pth:
        print(f'源路径: {folder_pth}\n提取路径: {tar_folder_pth}\n移动数量:{mov_cnt}')
    else:
        print(f'源路径: {folder_pth}\n移动数量: {mov_cnt}')

# folders = os.lisdir(root)
# for folder in folders:
#     folder_pth = os.path.join(root, folder)
#     if os.path.isdir(folder)

curDir, dirs, files = next(os.walk(root))
# print(sorted(dirs))
print(dirs)
# print(dirs.sort())
# print(dirs)
dirs.sort()

for dir in dirs:
    collect_photo_mov(os.path.join(root, dir), output_pth=output_pth)

# folder_pth = r'F:\myFiles\backup\221218\2023\202304'
# collect_photo_mov(folder_pth)


        # if '.MOV' in file:
        #     flag = (file[:-4] + '.PNG') in files or (file[:-4] + '.HEIC') in files
        #
        #
        #     if flag:
        #         file_pth = os.path.join(folder_pth, file)
        #         tar_folder = os.path.join(folder_pth, 'MOV')
        #
        #         if not os.path.exists(tar_folder):
        #             os.makedirs(tar_folder)
        #
        #         tar_pth = os.path.join(tar_folder, file)
        #
        #         shutil.move(file_pth, tar_pth)