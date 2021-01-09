#!/bin/bash

# Install script for crypto trading bot libraries
# Created on Sat Jan  9 09:56:48 2021


clear

echo "======================================================="
echo "========= Instantiating Virtual Environment ==========="
echo "======================================================="

read -r -p "This script will make changes to your system which may break some applications and may require you to reimage your SD card. Are you sure that you wish to continue? [y/N] " confirm

if ! [[ $confirm =~ ^([yY][eE][sS]|[yY])$ ]]
then
	exit 1
fi

clear
echo "Installing dos2Unix"

sudo apt-get install dos2unix

echo ""
echo "Converting files to Unix"

dos2unix *.py
dos2unix *.md
dos2unix *.txt

echo ""

echo "Building virtual environment and installing Python libraries"

sudo apt install python3-pip

pip3 install virtualenv
virtualenv crypto
source crypto/bin/activate

sudo apt-get install libatlas-base-dev

pip3 install cbpro==1.1.4
pip3 install numpy==1.16.5
pip3 install pandas==0.25.1

echo "All relevant Python libraries installed"

chmod +x run_bot.py

echo "Script is now executable"
echo "First update parameters.py file"
echo "Then execute ./run_bot.py"
echo "You are a great American!!"

exit 0
