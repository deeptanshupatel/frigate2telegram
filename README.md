# frigate2telegram
Python project to send frigate photos and video motion activated notifications to your telegram.

## How to use:
1. Copy config.yaml.example file and rename to config.yaml
2. Edit config.yaml with your information for "_REPLACE_"
    ```
    mqtt:
        host: _REPLACE_ # mqtt host/server like 192.168.1.203
        port: 1883 # mqtt host/server port

    telegram:
        chat_id: _REPLACE_ # your telegram chat id
        api_token: _REPLACE_ # your telegram bot api token

    frigate:
        host: _REPLACE_ # frigate host/server like 192.168.1.4
        port: 5001 # frigate host/server port
3. Run this command below
   ```
   sudo docker compose up -d

## If you want to build image yourself then follow steps below:
1. Clone the repo
    ```
    git clone https://github.com/deeptanshupatel/frigate2telegram.git
2. Rename config.yaml.example file to config.yaml
    ```
    mv config.yaml.example config.yaml
3. Edit config.yaml with your information for "_REPLACE_"
    ```
    mqtt:
        host: _REPLACE_ # mqtt host/server like 192.168.1.203
        port: 1883 # mqtt host/server port

    telegram:
        chat_id: _REPLACE_ # your telegram chat id
        api_token: _REPLACE_ # your telegram bot api token

    frigate:
        host: _REPLACE_ # frigate host/server like 192.168.1.4
        port: 5001 # frigate host/server port
4. Run this command below
   ```
   sudo docker compose up -d --build --force-recreate

Upcoming feature list:
1. Support frigate camera zones
2. Add docker support
