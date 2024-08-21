#!/bin/bash

if [ "$1" == "build" ]
then
pyinstaller --onefile --name epicexplorer-prism ./main.py
elif [ "$1" == "install" ]
then
pyinstaller --onefile --name epicexplorer-prism ./main.py
mv ./dist/epicexplorer-prism $HOME/.local/bin
else
echo 'Invalid Argument: {build, install}'
fi
