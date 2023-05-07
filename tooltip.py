from tkinter import *  

class ToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text="widget info"):
        self.waittime = 280    # miliseconds
        self.wraplength = 250  # pixels
        self.widget = widget
        self.text = text
        self.index = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        if self.widget.cget("state") == "disabled":
            return
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        widget_id = self.id
        self.id = None
        if widget_id:
            self.widget.after_cancel(widget_id)

    def showtip(self, event=None):
        x = y = 0
        try:
            if self.index:
                x, y, cx, cy = self.widget.bbox(self.index)
            else:
                x, y, cx, cy = self.widget.bbox("insert")
        except:
            pass
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+{:d}+{:d}".format(x, y))
        label = Label(
            self.tw,
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self.wraplength
        )
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
