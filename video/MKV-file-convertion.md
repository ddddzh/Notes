### Extract from mkv by track id
`mkvextract tracks 11.mkv 0:video.mp4 1:audio.mp3`

### Convert 264-10bit to 8bit
`ffmpeg -i input.avc -c:v libx264 -crf 18 -vf format=yuv420p -c:a copy output.mp4`
Use GPU for encoder
`ffmpeg -i video.avc -c:v libx264 -crf 18 -vf format=yuv420p -c:a copy -vcodec h264_nvenc video-8bit.mp4`

### Convert audio to aac
`ffmpeg -i audio.flac -acodec libfaac audio.aac`

### Merging video, audio and subs
`ffmpeg -i video.avc -i audio.flac -vf ass=sub.ass output.mp4`

### Using GPU to encode(Not support H264 10bit)
https://devblogs.nvidia.com/nvidia-ffmpeg-transcoding-guide/

`ffmpeg -vsync 0 -hwaccel cuvid -c:v h264_cuvid -i input.mp4 -c:a copy -c:v h264_nvenc output.mp4`

parameters' explanation:
- `-vsync 0`: prevents duplication or dropping of frames
- `-hwaccel cuvid`: keeps the decoded frames in GPU memory
- `-c:a copy`: copies the audio stream without any re-encoding
- `-c:v h264_cuvid`: selects the NVIDIA hardware accelerated H.264 decoder
- `-c:v h264_nvenc`: selects the NVIDIA hardware accelerated H.264 encoder

GPU can't merge sub layer with video layer. To do so, need to remove "-hwaccel cuvid", which means to use GPU memory instead of PC RAM.

`ffmpeg -vsync 0 -vcodec h264_cuvid -i 2-video.mp4 -i 2-audio.aac -acodec copy -vcodec h264_nvenc  -vf ass=sub.ass output.mp4`


### Compare video quality
Package itu-p1203
in folder, run "python3 -m itu-p1203 input_file.mp4"

CRF-18 is closer to the original result
```
{
 "origin.mp4": {
  "O23": 5.0,
  "O35": 4.976864837961674,
  "O46": 4.801464330885505,
  "date": "2020-05-03T03:10:45.444833",
  "mode": 1,
  "streamId": 42
 }
}
```
```
{
 "video.mp4": {
  "O23": 5.0,
  "O35": 4.843546917902638,
  "O46": 4.696263647077321,
  "date": "2020-05-03T03:11:08.490124",
  "mode": 1,
  "streamId": 42
 }
}
```
```
{
 "video-crf18.mp4": {
  "O23": 5.0,
  "O35": 4.922825133807513,
  "O46": 4.758133612173705,
  "date": "2020-05-03T03:11:29.387840",
  "mode": 1,
  "streamId": 42
 }
}
```
```
{
 "/mnt/c/z-seed/02-extraction/Ep01/final.mp4": {
  "O23": 5.0,
  "O35": 4.690607925109252,
  "O46": 4.557171096731328,
  "date": "2020-05-03T05:03:32.723736",
  "mode": 1,
  "streamId": 42
 }
}
```
```
{
 "/mnt/c/z-seed/02-extraction/Ep01/final-2.mp4": {
  "O23": 5.0,
  "O35": 4.6906037935496725,
  "O46": 4.557168056407765,
  "date": "2020-05-03T05:04:15.266397",
  "mode": 1,
  "streamId": 42
 }
}
```

### Check video bit depth
`ffprobe -loglevel panic -show_entries stream=bits_per_raw_sample -select_streams v input.mp4`
