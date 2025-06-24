:: Hide Command and Set Scope
@echo off

:: Customize Window
title Palworld Dedicated Server Manager
echo Setting up your environment...

:: Create a virtual environment
python -m venv venv

:: Activate the environment
call venv\Scripts\activate

:: Install the required packages
python -m pip install -r requirements.txt
python Server-Manager.py