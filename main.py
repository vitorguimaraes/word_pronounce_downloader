import os
import random
import string 
import tkinter as tk
import threading
from time import sleep
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage
from tkinter.messagebox import showinfo
from threading import Thread
import backend
from tooltip import ToolTip


class AsyncDownload(Thread):
    def __init__(self, word, file, filepath, accent, iid):
        super().__init__()

        self.word = word
        self.file = file
        self.filepath = filepath
        self.accent = accent
        self.iid = iid
        self.response = None

    def run(self):
        threading.Timer(0.5, self.request()) 

    def request(self):
        self.response = backend.download(self.word, self.filepath, self.accent)


def main():
    # Window
    root = tk.Tk()
    icon = PhotoImage(file = "icon.png")   
    root.iconphoto(False, icon)  

    style = ttk.Style()
    style.theme_use("clam")

    root.title("Macmillan Audio Downloader")
    window_width = 380
    window_height = 370

    # get the screen dimension
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # find the center point
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)

    # set the position of the window to the center of the screen
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.resizable(False, False)
    
    # ***** Functions *****
    def config_search():
        word = word_entry.get()
        uk_accent = uk_accent_check.get()
        us_accent = us_accent_check.get()
        save_at = save_at_entry.get()
        
        download_button["state"] = tk.DISABLED

        if "," in word: 
            word_list = word.replace(" ", "")
            word_list = word_list.split(",")
            word_list = [word for word in word_list if word != ""]

            for word in word_list: 
                handle_download(word, uk_accent, us_accent, save_at)
        else: 
            handle_download(word, uk_accent, us_accent, save_at)

        download_button['state'] = tk.NORMAL

    def handle_download(word, uk_accent, us_accent, save_at):

        if len(word) == 0:
            showinfo(title="Empty word", message="Word can't be empty")

        if uk_accent == "1" and len(word) > 0:
            file = word + "_Br.mp3"
            filepath = save_at + "/" + file
            iid = "iid_" + random.choice(string.ascii_letters) + str(random.randrange(1, 10000)) 

            tree.insert(parent="", iid=iid, index=tk.END, values=(word, file, "downloading"))

            download_thread = AsyncDownload(word, file, filepath, "uk_accent", iid)
            download_thread.start()
            monitor(download_thread)

        if us_accent == "1" and len(word) > 0:
            file = word + "_Am.mp3"
            filepath = save_at + "/" + file
            iid = "iid_" + random.choice(string.ascii_letters) + str(random.randrange(1, 10000)) 

            tree.insert(parent="", iid=iid, index=tk.END, values=(word, file, "downloading"))

            download_thread = AsyncDownload(word, file, filepath, "us_accent", iid)
            download_thread.start()
            monitor(download_thread)

    def handle_response(response, iid, word, file):
        if response[0] == 200 and iid in tree.get_children(): 
            tree.item(iid, values=(word, file, "success"))

        elif response[0] != 200 and iid in tree.get_children():
            tree.item(iid, values=(word, file, response[1]))

    def monitor(thread):
        if thread.is_alive():
                # check the thread every 100ms
                root.after(100, lambda: monitor(thread))
        else: 
            handle_response(thread.response, thread.iid, thread.word, thread.file)

    def browse():
        path = filedialog.askdirectory(title="Open Folder")
        save_at_path.set(path)

    def check_changed():
        uk_accent_value = uk_accent_check.get()
        us_accent_value = us_accent_check.get()

        if uk_accent_value == "0" and us_accent_value == "0":
            uk_accent_check.set("1")

    def clear_tree():
        for row in tree.get_children():
            tree.delete(row)  

    def callback(event):
        event.widget.select_range(0, "end")
        event.widget.icursor("end")
        return "break"

    # ***** Widgets *****
    frame = ttk.Frame(root)
    frame.grid(row=0, column=0)
    frame["padding"] = (12, 12, 12, 12)

    # Word to search
    word_label = ttk.Label(frame, text="Word")
    word_label.grid(row=0, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky=tk.W, columnspan=1)

    word = tk.StringVar()
    word_entry = ttk.Entry(frame, textvariable=word, width=22)
    word_entry.focus()
    word_entry.grid(row=0, column=1, padx=4, pady=0, ipadx=0, ipady=0, sticky=tk.W, columnspan=1)
    word_entry.bind("<Control-a>", callback)
    ToolTip(word_entry, "You can search for a single word or multiple words. \nFor example: \ncar, cat, dog, house")

    # Accent
    uk_accent_check = tk.StringVar(value="1")
    uk_check_box = ttk.Checkbutton(frame, text="British", variable=uk_accent_check, onvalue="1", offvalue="0", command=check_changed)
    uk_check_box.grid(row=0, column=2, padx=4, pady=8, ipadx=0, ipady=0, sticky=tk.W, columnspan=1)
    ToolTip(uk_check_box, "British accent")

    us_accent_check = tk.StringVar(value="0")
    us_check_box = ttk.Checkbutton(frame, text="American", variable=us_accent_check, onvalue="1", offvalue="0", command=check_changed)
    us_check_box.grid(row=0, column=3, padx=0, pady=0, ipadx=0, ipady=0, sticky=tk.W, columnspan=1)
    ToolTip(us_check_box, "American accent")

    # Save at
    save_at_label = ttk.Label(frame, text="Save")
    save_at_label.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W, columnspan=1)

    save_at_path = tk.StringVar(value=os.getcwd())
    save_at_entry = ttk.Entry(frame, textvariable=save_at_path, width=32)
    save_at_entry.grid(row=1, column=1, padx=4, pady=0, ipadx=0, ipady=0, sticky=tk.W, columnspan=2)
    save_at_entry.bind("<Control-a>", callback)
    ToolTip(save_at_entry, "Download folder path")

    folder_icon = tk.PhotoImage(file="folder.png")
    save_at_button = ttk.Button(frame, image=folder_icon, compound=tk.LEFT, text="Browse", width=6, command=browse)  
    save_at_button.grid(row=1, column=3, padx=4, pady=0, ipadx=0, ipady=0, columnspan=1)

    download_button = ttk.Button(frame, width=48, text="Download", command=config_search) 
    download_button.grid(row=2, column=0, padx=0, pady=8, ipadx=0, ipady=0, columnspan=4)

    # Tree
    tree = ttk.Treeview(frame, show="headings", height=8)
    tree["columns"]=("Word", "File", "Status")

    tree.column("#1", width=100)
    tree.column("#2", width=132)
    tree.column("#3", width=116)

    tree.heading("#1", text="Word")
    tree.heading("#2", text="File")
    tree.heading("#3", text="Status")

    tree.grid(row=3, column=0, padx=4, pady=0, ipadx=0, ipady=0, columnspan=4, sticky="NSEW")

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=3, column=3, pady=0, sticky="NSE")

    clear_button = ttk.Button(frame, width=6, text="Clear", command=clear_tree) 
    clear_button.grid(row=4, column=0, padx=4, pady=6, ipadx=0, ipady=0, sticky=tk.W, columnspan=2)

    root.mainloop()


if __name__ == "__main__":
    main()
