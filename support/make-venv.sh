#!/bin/bash

if [ $(which virtualenv) ]; then
	virtualenv --python=python3 venv

	if [ -d venv ]; then
		source venv/bin/activate
		if [ -f "requirements.txt" ]; then
			pip install -r "requirements.txt"
		fi
		deactivate
	fi
fi
