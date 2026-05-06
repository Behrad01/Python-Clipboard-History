# importing modules
import pyperclip
from pynput.keyboard import Key, Listener
import tkinter as tk
import json
from datetime import datetime

class ClipboardHistory:
    def __init__(self):
        # setting up the window
        self.window = tk.Tk()
        self.window.overrideredirect(True)  # no title bar or buttons             
        self.window.withdraw()  # hidden at start
        self.is_hidden = True  # track if window is visible

        # window size and centering
        self.width = 350
        self.height = 500
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f'{self.width}x{self.height}+{x}+{y}')

        # text box where clipboard history will be shown
        self.text_area = tk.Text(self.window, wrap=tk.WORD, height=29, width=50)
        self.text_area.pack(padx=5, pady=5)

        # variables to track clipboard stuff
        self.current_clipboard = ''
        self.clipboard_history = []
        self.window_hotkey = '`'  # ` toggles the window

        # starting the listener and clipboard monitor
        self.keyboard_listener()    
        self.get_clipboard()
        self.window.withdraw()  # hiding window
        self.window.mainloop()  # keep the app running

    def get_clipboard(self):
        # get whatever is in clipboard right now
        clipboard_content = pyperclip.paste()
        
        # cleaning up weird line endings (windows stuff)
        clipboard_content = clipboard_content.replace('\r\r\n', '\n')
        clipboard_content = clipboard_content.replace('\r\n', '\n')
        clipboard_content = clipboard_content.replace('\r', '\n')
        clipboard_content = clipboard_content.strip()
        
        # timestamp for when this was copied
        clipboard_content_time = datetime.now().strftime("%H:%M:%S")

        # load existing history from json file
        try:
            with open('clipboard.json', 'r') as file:
                self.clipboard_history = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.clipboard_history = []  # start fresh if file is missing or broken

        # only save if it's new content
        if clipboard_content != self.current_clipboard:
            self.clipboard_history.append([clipboard_content_time, clipboard_content])
            if len(self.clipboard_history) > 5:  # keep only last 5 items
                self.clipboard_history.pop(0)

            # save to json file
            with open('clipboard.json', 'w') as file:
                json.dump(self.clipboard_history, file)
        
        # update current clipboard so we don't save duplicates
        self.current_clipboard = clipboard_content

        # check again after 100ms
        self.window.after(100, self.get_clipboard)

    def hide_window(self):
        # hide the window
        self.window.after(0, self.window.withdraw)
        self.is_hidden = True

    def show_window(self):
        # show the window
        self.window.after(0, self.window.deiconify)
        self.is_hidden = False

        # clear old stuff from text box
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(padx=10, pady=10)     
        self.text_area.tag_configure('line_indent', lmargin1=20, lmargin2=25)

        # loop through history and display each item with number and timestamp
        for index, content in enumerate(self.clipboard_history, 1):              
            timestamp = content[0]
            text = content[1]

            spacing = ' ' * 10  # just for looks between number and timestamp

            self.text_area.insert(tk.END, f"{index}. {spacing}{timestamp}{spacing}\n")
            self.text_area.insert(tk.END, f"{text}\n\n\n", "line_indent")       

    def keyboard_listener(self):
        # listens for key presses (runs in background)
        def on_press(k):
            try:
                key = k.char  # normal letter keys
            except AttributeError:
                key = k  # special keys like tab

            # if ` is pressed, toggle window visibility
            if key == self.window_hotkey:
                if self.is_hidden:
                    self.show_window()
                else:
                    self.hide_window()

        # start the listener in daemon thread (runs quietly in background)
        Listener(on_press=on_press, daemon=True).start()

# run the code
if __name__ == '__main__':
    Window = ClipboardHistory()
