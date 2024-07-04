# Custom Event Notication from Frigate NVR to Signal
This is my setup that includes running Frigate NVR through a Google Coral TPU. It sends events to an Apache Mosquitto MQTT broker.  From there, I have a python script called "send_message" that reads from the `frigate/events` MQTT topic and when the right message comes through, it will grab the thumbnail image of the event from the Frigate HTTP API and send that to signal-cli-rest-api for delivery to a Signal recipient.

## Setup

1. Checkout this git repo

2. Create your Frigate config in `./frigate/conf/conf.yml`. Mine looks something like this:
    ```
    detectors: # <---- add detectors
      coral:
        type: edgetpu
        device: usb

    cameras:
      front: # <------ Name the camera
        enabled: True
        ffmpeg:
          inputs:
            - path: rtsp://blah@1.1.1.1/live0 # <----- The stream you want to use for detection
              roles:
                - detect
                - record
          hwaccel_args: preset-vaapi
        detect:
          enabled: True # <---- disable detection until you have a working camera feed
        record: # <----- Enable recording
          enabled: True
          retain:
            mode: all
          events:
            retain:
              mode: active_objects
        snapshots:
          enabled: True
          crop: True

    objects:
      filters:
        person:
          min_area: 2500

    timestamp_style:
      format: "%m/%d/%Y %H:%M:%S%Z"
      effect: "shadow"

    mqtt:
      enabled: True
      host: mqtt
      topic_prefix: frigate
      client_id: frigate
    ```

2. Build send_message Docker image
    ```
   cd send_message
   sudo docker build -t send_message .
   ```

3. Run signal-cli-rest-api once just to link your Signal Number
    1. Register for Signal, if you haven't already and create a group that all your NVR messages will go to.
    2. Run the signal-cli-rest-api docker image seperately just once to link it to your Signal account
     ```
     mkdir ./signal-cli-config
     sudo docker run --name signal-api --rm -p 8080:8080 \
       -v ./signal-cli-config:/home/.local/share/signal-cli \
       -e 'MODE=native' bbernhard/signal-cli-rest-api
     ```
   3. Follow the instructions in https://github.com/bbernhard/signal-cli-rest-api/tree/master to link your Signal Number
   4. Point a browser or curl to `http://localhost:8080/v1/groups/<number>`, and find the group id of the Signal group you just created.  It should look like `group.somethingsomethingsomething`.
   5. Close the signal-cli-rest-api docker terminal to close and delete the container

4. Create `.env` file in this directory with the following values
   ```
   SIGNAL_NUMBER="+15555555555" (substitute with your number!)
   SIGNAL_RECIPIENT="GROUP ID" (substitute with the group id you retrieved from above)
   ```

5. Run everything
In this directory, run:
   ```
   sudo docker compose up -d
   ```

## Working with the Setup
If you need to change anything in this setup, here are some helpful info.

* If you need to modify the send_message script, edit the `send_message/send_message.py` file.  Remember to run `sudo docker build -t send_message .` __inside the send_message directory__` to rebuild the Docker image.  Then you'll need to do a `sudo docker compose down` on the root directory and a `sudo docker compose up -d` to recreate the whole setup with the new send_message code.

* If you only need to update Frigate configs (which you should or you'll be using my camera settings), then you need to update `frigate/conf/conf.yaml`.  Then run `sudo docker compose restart` on the root directory.

* Similarly, if you need to update the Mosquitto configs, edit `mosquitto/conf/mosquitto.conf` and restart using docker compose with the command in the previous bullet point.


