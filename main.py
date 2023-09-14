# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 10:35:17 2023

@author: thiesesh
"""

import os
import PySimpleGUI as sg
import download

application_path = os.path.dirname(os.path.abspath(__file__))

# Layout definition
sg.theme('LightPurple')

text_size = (12, 1)
btn_size = (6, 1)

layout = [
    [
     [sg.Text("URL:", size = text_size),
      sg.InputText(key = "-URL-"),
      sg.Button("Clear", key = "-CLEARURL-", size = btn_size)],
     [sg.Text("Login token:", size = text_size),
      sg.InputText(key = "-TOKEN-"), 
      sg.Button("?", key = "-HELP-", size = btn_size)],
     [sg.Text("Directory:", size = text_size),
      sg.InputText(key = "-DIR-"), 
      sg.FolderBrowse(key = "-SELECTDIR-", size = btn_size)]
     ],
    [sg.Push(), sg.Button("Download", key = "-DL-"), sg.Push()]
]

def help_popup():
    help_text = """To download paid content, you need to be logged in. 
How you can find your login token depends on your browser.
But generally, the following should work: 

Right click on the Missevan website and click "Inspect". 
Select the "Storage" tab and take a look at the cookies. 
There should be an entry called "token". 
The value of this entry is a long string of numbers and letters. This is your login token."""
    
    popup_layout = [
        [sg.Image(os.path.join(application_path, "img/help.png"))],
        [sg.Text(help_text)],
        [sg.Push(), sg.OK(), sg.Push()]
    ]
    sg.Window('Login Token', popup_layout, font = ("Arial", 11)).read(close = True)

# Create the Window
window = sg.Window('Missevan Downloader', layout, font = ("Arial", 11))
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    # Delete URL from text field
    if event == "-CLEARURL-":
        window["-URL-"].update(value = "")
    # Update directory text field if directory is selected in file dialog
    if event == "-HELP-":
        help_popup()
    if event == "-SELECTDIR-":
        window["-DIR-"].update(value = values["-SELECTDIR-"])
    # Download stuff
    if event == "-DL-":
        download.download(values["-URL-"], values["-TOKEN-"], values["-DIR-"])
    # Close window
    if event == sg.WIN_CLOSED:
        break

window.close()