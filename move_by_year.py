import os
import shutil
import re
from tqdm import tqdm

root = '../230427_iphone'
tar_path = '../'


def move_by_year(root, tar_path):
	"""
	lms230429:
	:param root: 需要按年分类的（照片、视频）文件所在路径
	:param tar_path: 需要创建年份文件夹的路径，自动创建年份文件夹，如果已存在则直接移动进去
	:return:
	"""
	files = os.listdir(root)
	print(files)

	ptn = r'20\d\d'

	for file in tqdm(files):
		file_path = os.path.join(root, file)

		if not os.path.isfile(file_path):
			continue

		match = re.search(ptn, file)

		if not match:
			continue

		# print(match)
		# print(match.group())
		tar_folder = match.group()
		# 获得该照片所属年份

		# print(tar_folder)

		if not os.path.exists(tar_folder):
			os.makedirs(tar_folder)	# 创建年份文件夹

		tar_file_path = os.path.join(tar_path, tar_folder, file)
		shutil.move(file_path, tar_file_path)

move_by_year(root, tar_path)

