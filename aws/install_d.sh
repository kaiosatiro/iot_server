#!/bin/bash
sudo apt update
sudo apt-get install docker.io -y
sudo apt-get install docker-compose-v2 -y
sudo apt-get install nginx certbot
sudo apt-get install python3-certbot-nginx
sudo apt-get install make

sudo systemctl enable ufw
sudo ufw allow 'Nginx full'
sudo ufw allow Openssh

