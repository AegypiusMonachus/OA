#!/usr/bin/env python3

import os
import shutil

queue = [os.curdir]
while queue:
	path = queue.pop()
	path = os.path.abspath(path)
	path = os.path.normpath(path)
	path = os.path.normcase(path)
	for filename in os.listdir(path):
		filename = os.path.join(path, filename)
		if not os.path.isdir(filename):
			if filename.endswith('.pyc'):
				os.remove(filename)
			continue
		if filename.endswith('__pycache__'):
			shutil.rmtree(filename)
			continue
		if not filename.endswith('venv'):
			queue.append(filename)
