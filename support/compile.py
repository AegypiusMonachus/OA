#!/usr/bin/env python3

import os
import py_compile

queue = ["app"]
while queue:
	path = queue.pop()
	path = os.path.abspath(path)
	path = os.path.normpath(path)
	path = os.path.normcase(path)
	for filename in os.listdir(path):
		filename = os.path.join(path, filename)
		if os.path.isdir(filename):
			queue.append(filename)
			continue
		if filename.endswith('.py'):
			target = filename + 'c'
			py_compile.compile(filename, target)
