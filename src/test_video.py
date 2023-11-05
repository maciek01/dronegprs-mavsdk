#!/usr/bin/env python

import time
import video_manager



video_manager.init("raspivid -o - -t 0 -vf -hf -w 640 -h 480 -fps 10  | ffmpeg -f h264 -thread_queue_size 256 -i - -vcodec copy -an -f flv rtmp://home.kolesnik.org/dash/stream")



video_manager.toggleVid(None)
time.sleep(30)
video_manager.toggleVid(None)



