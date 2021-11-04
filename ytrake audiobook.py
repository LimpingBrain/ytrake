import tkinter as tk
import re
import subprocess
import threading
import time
import os
import string
from mutagen.mp4 import MP4
import mutagen
import shutil

#add method to pick only some vids from playlist
#add mutiple format options, add single video option
#chose video or audio option

def __init_edit(save_dir, edit_dir):
        edit_dir = edit_dir.replace("\n", "")
        save_dir = save_dir.replace("\n", "")
        print(edit_dir)
        print(save_dir)
        files = [f for f in os.scandir(edit_dir) if os.path.isfile(f)]
        for f in files:
            old_filename=str(f.name)
            filename=str(f.name)
            print("Trying to edit: "+filename)
            f_extns = filename.split(".")
            index = len(f_extns)
            exten=(f_extns[-1])#saves file extention
            filename = ''.join(map(str, f_extns[:index-1]))# makes file name of all items but the extension, removes extra periods
            if exten == "m4a":
                print("Editing tags on file #"+filename)
                f_extns = filename.split("^")#Splits file name values
            
                track = str(f_extns[0])#breaks list into variables
                playlist = str(f_extns[1])
                artist = str(f_extns[2])
                title = str(f_extns[3])
                date = str(f_extns[4])

                song=edit_dir+"\\"+old_filename
                update_tags(song, title, playlist, artist, artist, "Audio Book", make_date(date), track)

                print("Changing filename: "+filename)
                new_name=save_dir+artist+"\\"+playlist+"\\"+title+"."+exten
                new_folder=save_dir+artist+"\\"+playlist+"\\"
                file_name(song, new_name, new_folder, old_filename)
                
            else:
                print("Wrong file type: "+exten+" file needs to be m4a!")
                time.sleep(0.001) 

def file_name(old_name, new_name, new_folder, filename):
        if os.path.isfile(new_name) is False:
        #if file_name not in files :
                print("Renaming: "+old_name+" to: "+new_name)
                if not os.path.exists(new_folder):
                        os.makedirs(new_folder)
                        os.rename(old_name, new_name)
                else:
                        os.rename(old_name, new_name)
        else:
                print(new_name+" is already in folder")
                
##make date into something a bit more readable
def make_date(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8]
    date = day+month+year
    print (date)
    return date

## for future use
##def delete_tags(song):
##    #delete all tags from song
##    audio = mutagen.File(song, easy=True)
##    audio.clear()
##    audio.save(song)

##update tags with values from file
def update_tags(song, title, album, artist, album_artist, genre, date, track_number):
    #Update tags in song
    audio = mutagen.File(song, easy=True)
    audio["title"] = title
    audio["album"] = album
    audio["artist"] = artist
    audio["albumartist"] = album_artist
    audio["genre"] = genre
    audio["date"] = date
    audio["tracknumber"] = track_number
    audio.save()
       


class Hyperlink(tk.Label):
    def __init__(self, *args, url="", text=""):
        tk.Label.__init__(self, *args)
        
        self.url = url
        self.text = text
        if not text:
            self.text = self.url
            
        self.config(fg="blue", cursor="hand2", font='Verdana, 10', text="{}".format(self.text))
        self.bind("<Button-1>", lambda e: webbrowser.open_new(r"{}".format(url)))
        self.bind("<Enter>", lambda e: e.widget.config(font='System, 10 underline'))
        self.bind("<Leave>", lambda e: e.widget.config(font='System, 10'))


class Entrybox(tk.Frame):
    def __init__(self, *args, title="", default_val=False):
        tk.Frame.__init__(self, *args)
        title_label = tk.Label(self, text=title, font='Verdana, 10 italic'); title_label.pack(anchor='w')
        self.entry_box = tk.Text(self, height=1, font='Verdana, 10', bg='#FFFFFF'); self.entry_box.pack()
        self.entry_box.bind('<Return>', self.dummy_function)
        self.entry_box.bind("<Control-Key-a>", self.select_all)
        if default_val:
            self.entry_box.insert(tk.END, default_val)
    
    def get(self):
        return self.entry_box.get("1.0", tk.END)
        
    def select_all(self, event):
        self.entry_box.tag_add(tk.SEL, "1.0", tk.END)
        self.entry_box.mark_set(tk.INSERT, "1.0")
        self.entry_box.see(tk.INSERT)
        return 'break'
            
    def dummy_function(self, event):  # disable return on text widget
        return 'break'


def stream_process(process, save_dir, temp_dir, stat_var=None):
    go = process.poll() is None
    old_line = ""
    for line in process.stdout:
        print(line.decode())
        if "Finished" in line.decode():
            old_line = "Finished download."
            line = "Finished download"
            if old_line == "Finished download.":
                stat_var.set("Editing Metadata....")
                __init_edit(save_dir, temp_dir)
                old_line = "Completed."
                line = "Completed"
        stat_var.set(old_line)
        old_line = line
    return go

def download(playlist, save_dir, stat_var):
    temp_dir=save_dir+"temp"
    process = subprocess.Popen("".join(['yt-dlp_x86 --extract-audio --audio-format m4a --yes-playlist --embed-thumbnail "{}" -o "{}/'.format(playlist, temp_dir),'%(playlist_index)s^%(playlist)s^%(channel)s^%(title)s^%(upload_date)s.%(ext)s"']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while stream_process(process, save_dir, temp_dir, stat_var=stat_var):
        time.sleep(0.001)

class Mainframe(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.status_var = tk.StringVar(); self.status_var.set("")
        title_label = tk.Label(self, text="Ytrake Unleashed", font='Verdana, 30 bold'); title_label.pack()
        version_label = tk.Label(self, text="{}".format(self.master.VERSION), font='Verdana, 10 bold'); version_label.pack()
        license_label = tk.Label(self, text="Project distributed under MIT license", font='Verdana, 8 bold'); license_label.pack()
        github_label = Hyperlink(self, url="https://github.com/LimpingBrain/ytrake", text="https://github.com/LimpingBrain/ytrake"); github_label.pack()
        
        space = tk.Label(self); space.pack(pady=5)
        
        playlist_field = Entrybox(self, title="Playlist URL"); playlist_field.pack(pady=5)
        save_directory = Entrybox(self, title="Save Directory", default_val=str("G:\\AudioBook\\").split(str(__file__).split("\\")[-1])[0]); save_directory.pack(pady=5)
        
        space = tk.Label(self); space.pack(pady=5)
        
        #artist_name = Entrybox(self, title="Artist Name"); artist_name.pack(pady=5)
        
        download_button = tk.Button(self, text="Download", font='Verdana, 15 italic', width=15, command=lambda: self.__init_download(playlist=playlist_field.get(), save_dir=save_directory.get(), stat_var=self.status_var)); download_button.pack(anchor='w', pady=10)
        #edit_button = tk.Button(self, text="Edit", font='Verdana, 15 italic', width=15, command=lambda: self.__init_edit(edit_dir=save_directory.get(), stat_var=self.status_var)); edit_button.pack(anchor='w', pady=10)
        
        status_label = tk.Label(self, textvariable=self.status_var, font='Verdana, 10'); status_label.pack(anchor='w', pady=15)

    def __init_download(self, playlist="", save_dir="", stat_var=None):
        playlist = playlist.replace("\n", ""); save_dir = save_dir.replace("\n", "")
        stat_var.set("downloading....")
        threading.Thread(target=download, args=(playlist, save_dir, stat_var, )).start()  
            

class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self); self.geometry("640x640"); self.tk_setPalette(background="#DDDDDD")
        self.VERSION = "v1.1"
        Mainframe(self).pack(fill='both', expand=True, padx=25, pady=25)
        self.mainloop()

 

if __name__ == "__main__":
    App()
