#!/bin/bash


git fetch --all
git reset --hard origin/develop

if [ -d venv ]; then
	source venv/bin/activate
	pip install -r requirements.txt
	deactivate
fi

if [ -d venv ]; then
	source venv/bin/activate
	python support/compile.py
	deactivate

	find app -name "*.py" | xargs rm -rf
fi
