#!/bin/bash

install_dir="/usr/local/bin"
base_url="https://api.github.com/repos/mozilla/geckodriver/releases/latest"
json_response=$(curl -s $base_url)
tag_name=$(echo $json_response | jq -r '.tag_name')
os="linux64"
filename="geckodriver-${tag_name}-${os}.tar.gz"
download_link=$(echo $json_response | jq -r --arg FILENAME $filename '.assets[] | select(.name == $FILENAME) | .browser_download_url')
curl -s -L $download_link | tar -xz 
mv geckodriver $install_dir
