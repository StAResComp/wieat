#!/bin/bash

POSTGRES_PW=""
SECRET_KEY=""

HOME="/home/fishing"

# The production directory
TARGET="$HOME/fishing"

# A temporary directory for deployment
TEMP="$HOME/fishing.tmp"

# The Git repo
SOURCE="$HOME/fishing.source"

# Deploy the content to the temporary directory
cp -r $SOURCE $TEMP

cd $TEMP
sed -i "s/POSTGRES_PW_HERE/$POSTGRES_PW/g" fishing/settings.py
sed -i "s/SECRET_KEY_HERE/$SECRET_KEY/g" fishing/settings.py
sed -i "s/DEBUG\s*=\s*True/DEBUG = False/g" fishing/settings.py
python3 -m venv env
source env/bin/activate
pip3 install wheel
pip3 install psycopg2-binary
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic
deactivate

# Replace the production directory
# with the temporary directory
cd $HOME
rm -rf $TARGET
mv $TEMP $TARGET
