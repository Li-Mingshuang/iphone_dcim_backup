import os
import shutil
import re
from tqdm import tqdm

year = '2023'
root = fr'E:\myFiles\backup\221218\{year}'
tar_path = './'

def move_by_month(root, year, tar_path=None):
    """
    lms230429:
    :param root: 要按月分类的照片/视频所在路径（通常是年份文件夹）
    :param year: 要分类的照片/视频所属年份，用于正则表达式读取照片、视频文件的月份
    :param tar_path: 月份文件夹默认生成在当前文件夹（年份）路径下
    :return:
    """
    files = os.listdir(root)
    print(files)

    ptn = fr'{year}\d\d'

    for file in tqdm(files):
        if not os.path.isfile(os.path.join(root, file)):
            continue

        match = re.search(ptn, file)

        # print(match)
        # print(match.group())
        if not match:
            continue

        tar_folder = match.group()  # 获取月份
        tar_folder = os.path.join(root, tar_folder) # 月份文件夹路径
        # print(tar_folder)
        if not os.path.exists(tar_folder):
            os.makedirs(tar_folder)

        file_path = os.path.join(root, file)
        tar_path = os.path.join(tar_folder, file)

        shutil.move(file_path, tar_path)

move_by_month(root, year)