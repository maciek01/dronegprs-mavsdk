# dronegprs-mavsdk
port of https://github.com/maciek01/dronegprs for px4 mavsdk


Goal of the project is to establish 2 way control between ground station server and a fleet of UAVs (drones, planes, ...) leveraging GSM GPRS based data networks.

The idea is to enable governmental institutions to autonomously deploy drones in event of minor scale emergencies with ability to monitor and control the deployment of each indivudual UAV.

Scope of POC:

Each UAV will be equipped with MAVlink compatible flight controller, GPS module, Raspbery PI connected to USB GPRS modem. Raspberry pie will host the following software: MAVSDK, custom developed status reporting service, as well as custom RESTfull server to enable processing of ground station commands.

"Ground station" is based on an HTTP RESTfull service deployed and available via public internet.

Each UAV will report its stats (position, speed, altitude, heading, battery state, etc.) to the ground station via HTTP client.

Groud station will allow operatios to monitor/visualize each UAV status/location, and command it remotely (via REST service deployed onboard). Examples of command: land immediately, return to home/abord the mission, deploy payload, alter course/go to waypoint, alter mission, swarm, travel to another UAV.

ground station console: http://home.kolesnik.org:8000/map.html



SETUP

1. Run camera test:

On Bullseye and later OSes:

Make sure to disable legacy camera then restart RPi.
Test the camera:
```
libcamera-vid -t 10000 -o test.h264
```

It shoudl capyture 10 secs of jmpeg video

2. Run:
```
bin/update-pi.sh
```
3. Run:
```
bin/install.sh
```
4. Run
```
bin/setup.sh
```
5. Follow steps in [uart.readme.md](./uart.readme.md)


Video and streaming tests:

VIDEO STREAM VALIDATION (requiers gst - part of the install.sh script)
```
gst-launch-1.0 -e -v udpsrc port=3333 ! application/x-rtp, encoding-name=JPEG, payload=26 ! rtpjpegdepay ! jpegdec ! autovideosink
```
or
```
libcamera-vid -v 0 -t 0 --nopreview --framerate 15 --codec mjpeg --bitrate 2500000 --profile baseline --rotation 180  --width 640 --height 480 --inline -o -|gst-launch-1.0 fdsrc ! jpegparse ! rtpjpegpay ! udpsink host=<web rtc host - ex: janus> port=3333
```

Also, with bullseye onwards, you can test streaming to a destinaction (say, vlc on your laptop):
```
libcamera-vid -v 0 -t 0 --nopreview --rotation 180  --inline -o udp://<destination ip>:3333
```



