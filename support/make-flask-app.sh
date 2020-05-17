#!/bin/bash


function createApp() {
	mkdir "app"; cd "app"
		touch "__init__.py"

		mkdir "static"
		mkdir "static/css"
		mkdir "static/js"
		mkdir "templates"
	cd ..
}


function createConfig() {
	touch "config.py"
}


function createManager() {
	touch "manager.py"
}


function createModels() {
	mkdir "models"; cd "models"
		touch "__init__.py"

		mkdir "common"; cd "common"
			touch "__init__.py"
		cd ..
	cd ..
}


function createCommon() {
	mkdir "common"; cd "common"
		touch "__init__.py"
	cd ..
}


function createExtensions() {
	touch "extensions.py"
}


function createTests() {
	mkdir "tests"; cd "tests"
	cd ..
}


function createFunctionalTests() {
	mkdir "functional-tests"; cd "functional-tests"
	cd ..
}


function createWSGI() {
	mkdir "uwsgi"; cd "uwsgi"
		touch "uwsgi.ini"
	cd ..
}


function createSupport() {
	mkdir "support"; cd "support"
	cd ..
}


function createBlueprint() {
	mkdir $1; cd $1
		touch "__init__.py"
		touch "errors.py"
		touch "views.py"
	cd ..
}


function createAPI() {
	mkdir $1; cd $1
		touch "__init__.py"
		touch "errors.py"

		mkdir "resources"; cd "resources"
			touch "__init__.py"
		cd ..

		mkdir "common"; cd "common"
			touch "__init__.py"
		cd ..
	cd ..
}


createApp

cd "app"
	createModels
	createCommon
	createExtensions

	createAPI "api"
	createBlueprint "main"
	createBlueprint "auth"
cd ..

createConfig
createManager
createTests
createFunctionalTests
createWSGI
createSupport
