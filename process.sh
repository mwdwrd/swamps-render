#!/bin/bash
path="videos"
assets="assets"

for file in `cd ${path};ls -1 ${file}` ;do
  chunk=${file%%.*}

  # convert image sequence to mp4
  yes | ffmpeg -r 30 -f image2 -s 1080x1080 -i "${path}/${chunk}/${chunk}_%05d.png" -vcodec libx264 -crf 5 -pix_fmt yuv420p "${path}/${chunk}_x1.mp4"
  
  # loop twice
  yes | ffmpeg -stream_loop 1 -i "${path}/${chunk}_x1.mp4" -c copy "${path}/${chunk}.mp4"

  # Add Audio
  # yes | ffmpeg -i "${path}/${chunk}/${chunk}.mp4" -i "${assets}/audio/gen1.mp3" -c:a copy -shortest "${path}/${chunk}/${chunk}_audio.mp4"

  # remove single loop
  # rm "${path}/${chunk}_x1.mp4"

  # convert to webm double pass
  yes | ffmpeg -i "${path}/${chunk}.mp4" -b:v 0 -crf 30 -pass 1 -an -f webm /dev/null
  yes | ffmpeg -i "${path}/${chunk}.mp4" -b:v 0 -crf 30 -pass 2 "${path}/${chunk}.webm"
done
