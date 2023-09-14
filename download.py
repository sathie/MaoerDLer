# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 12:04:46 2023

@author: thiesesh
"""

import re
import json
import requests
import os
import PySimpleGUI as sg

def retrieve(url, cookies):
    r = requests.get(url, cookies)
    if r.status_code == 200:
        return r.content
    else:
        sg.popup_error(f"{url}\n\nhas returned error code {r.status_code}",
                       title = "Error!")
        return None

def download(url, token, directory):
    # Extract sound ID from url
    matchobj = re.search(r"(?<=id=)\d+$", url)
    
    if not matchobj:
        sg.popup_error("Not a valid missevan url", title = "Error!")
        return False
    
    sound_id = matchobj[0]
    
    # Set cookies
    cookies = {}
    if token:
        cookies["token"] = token
    
    # Get info
    info_url = f"https://www.missevan.com/sound/getsound?soundid={sound_id}"
    info = retrieve(info_url, cookies)
    
    info = json.loads(info).get("info", {}).get("sound")
    title = info.get("soundstr")
    sound_url = info.get("soundurl")
    video_url = info.get("videourl")
    subtitle_url = info.get("subtitle_url")
    
    # Create directory
    if os.path.exists(directory):
        os.chdir(directory)
        if not os.path.exists(title):
            os.makedirs(title)
        os.chdir(title)
    else:
        sg.popup_error("Directory doesn't exist.", title = "Error!")
    
    # Save sound
    if sound_url:
        sound = retrieve(sound_url, cookies)
        if sound:
            with open("sound.m4a", "wb") as file:
                file.write(sound)
    
    # Save video
    if video_url:
        video = retrieve(video_url, cookies)
        if video:
            with open("video.mp4", "wb") as file:
                file.write(video)
    
    # Save subtitles
    if subtitle_url:
        subs = retrieve(subtitle_url, cookies)
        if subs:
            subs = json.loads(subs)
            filename = "subs.json"
            with open(filename, "w") as file:
                json.dump(subs, file)
            
            # Also dump srt
            filename = title + "_subs.srt"
            filename = title + "_subs_fmt.srt"
    
    # Get images
    imgurl = f"https://www.missevan.com/sound/getimages?soundid={sound_id}"
    if imgurl:
        r_img = requests.get(imgurl, cookies = cookies)
        if r_img.status_code == 200:
            info_img = json.loads(r_img.content).get("successVal", {}).get("images", [])
            
            if len(info_img) > 1:
                print("More than one image... it's a slideshow.")
            
            for img in info_img:
                r_image = requests.get(img[0], cookies = cookies)
                file_ending = img[0].split(".")[-1]
                filename = img[5] + "." + file_ending
                with open(filename, "wb") as file:
                    file.write(r_image.content)

    return True