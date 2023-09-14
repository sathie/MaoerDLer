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
import srt
import csv

class Session(requests.Session):
    def __init__(self, cookies):
        super().__init__()
        _ = self.get("https://missevan.com", cookies = cookies)
        
    def retrieve(self, url):
        r = self.get(url)
        if r.status_code == 200:
            return r.content
        else:
            sg.popup_error(f"{url}\n\nhas returned error code {r.status_code}",
                           title = "Error!")
            return None

def download(url, token, directory):
    """ Download all available files from site and save """
    # Extract sound ID from url
    matchobj = re.search(r"(?<=id=)\d+$", url)
    
    if not matchobj:
        sg.popup_error("Not a valid missevan url", title = "Error!")
        return False
    
    sound_id = matchobj[0]
    
    # Set cookies and create session
    cookies = {}
    if token:
        cookies["token"] = token
    session = Session(cookies)
    
    # Get info
    info_url = f"https://www.missevan.com/sound/getsound?soundid={sound_id}"
    info = session.retrieve(info_url)
    
    info = json.loads(info).get("info", {}).get("sound")
    title = info.get("soundstr")
    sound_url = info.get("soundurl")
    video_url = info.get("videourl")
    subtitle_url = info.get("subtitle_url")
    
    # Create directory
    if os.path.exists(directory):
        new_dir = os.path.join(directory, title)
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
    else:
        sg.popup_error("Directory doesn't exist.", title = "Error!")
        return False
    
    # Save sound
    if sound_url:
        sound = session.retrieve(sound_url)
        if sound:
            print("Sound file found")
            filepath = os.path.join(new_dir, "sound.m4a")
            with open(filepath, "wb") as file:
                file.write(sound)
    
    # Save video
    if video_url:
        video = session.retrieve(video_url)
        if video:
            print("Video file found")
            filepath = os.path.join(new_dir, "video.mp4")
            with open(filepath, "wb") as file:
                file.write(video)
    
    # Save subtitles
    if subtitle_url:
        subs = session.retrieve(subtitle_url)
        if subs:
            print("Subtitles found")
            subs = json.loads(subs)
            
            # Dump raw subs
            filepath = os.path.join(new_dir, "subs.json")
            with open(filepath, "w") as file:
                json.dump(subs, file)
            
            # transform times and color
            subs_transformed = srt.transform(subs)
            
            # Also dump srt
            srt_no_fmt = srt.to_srt(subs_transformed, False)
            filepath = os.path.join(new_dir, "subs.srt")
            with open(filepath, "w", encoding = "UTF8") as file:
            	file.write(srt_no_fmt)
            	
            srt_fmt = srt.to_srt(subs_transformed, True)
            filepath = os.path.join(new_dir, "subs_fmt.srt")
            with open(filepath, "w", encoding = "UTF8") as file:
            	file.write(srt_fmt)
                
            # Also dump csv
            header = ["role_cn", "text_cn",
                      "start_time", "end_time",
                      "color", "italic", "underline"]
            subs_table = srt.to_table(subs_transformed)
            filepath = os.path.join(new_dir, "subs.csv")
            with open(filepath, "w", encoding = "UTF8", newline = "") as file:
                writer = csv.writer(file)
                writer.writerow(header)
                writer.writerows(subs_table)
    
    # Get images
    imgurl = f"https://www.missevan.com/sound/getimages?soundid={sound_id}"
    if imgurl:
        r_img = session.retrieve(imgurl)
        if r_img:
            # Get image info file and sort according to timestamp
            info_img = json.loads(r_img).get("successVal", {}).get("images", [])
            info_img = sorted(info_img, key=lambda x: x[1])
            
            # Download images and save
            for num, img in enumerate(info_img):
                image_content = session.retrieve(img[0])
                file_ending = img[0].split(".")[-1]
                filename = f"img_{num:03}" + "." + file_ending
                img[0] = filename
                filepath = os.path.join(new_dir, filename)
                with open(filepath, "wb") as file:
                    file.write(image_content)
            
            # If slideshow: save as csv
            if len(info_img) > 1:
                filepath = os.path.join(new_dir, "slideshow.csv")
                with open(filepath, "w", encoding = "UTF8") as file: 
                    writer = csv.writer(file)
                    header = ["filename", "time", "width", "height", "idk",
                              "title", "idk", "idk"]
                    writer.writerow(header)
                    writer.writerows(info_img)
    return True
