# TOOL: Audio Detection from Video
### This Simple tool help the user to rename the video based on the song (audio) in the video once the user input the path of designated folder

## Features 
This is the simple tool that help the user:  
1) detect the song from the Video 
2) rename the Video based on the name of the song

The code using [shazamIO](https://github.com/shazamio/ShazamIO) to identify the song.

## How to use
1. Make sure the Videos with mp4 formate are in the designated folder
2. Copy the path of the folder then paste to the main.py file
3. Waiting for identification. Due to the rate limit of shazamIO, the user can only detect 3 songs per min.
4. Once all the song are identified, the name of video will be named based on: "NameOfSong + Time"
5. If the song cannot be identified from the audio of the video, then the name of video will not be changed. 
