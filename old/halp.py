# https://stackoverflow.com/posts/35566389

from tkinter import *

class zoomer(Tk):

    def __init__(self):
        x=100
        y=100
        Tk.__init__(self)
        self.border = 10
        self.size_x = x
        self.size_y = y

        #SIZE
        self.app_sizex = 200
        self.app_sizey = 200
        fontSize=int(x/20)

        self.title("Graphic")
        self.geometry(str(self.app_sizex+10) + "x" + str(self.app_sizey+40))

        #CANVAS + BORDER
        self.canvas = Canvas(self, width = self.app_sizex, height = self.app_sizey, scrollregion=(0,0,x,y))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.create_line(self.border, self.border, self.border, y-self.border)
        self.canvas.create_line(x-self.border, self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border,   self.border, x-self.border, self.border)
        self.canvas.create_line(self.border, y-self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border,   self.border, x-self.border, y-self.border)
        text1=self.canvas.create_text(50, 50, fill="white",font=("Purisa", fontSize))
        self.canvas.itemconfig(text1, text="Graphic Text")

        #SCROLLING BARS
        self.vbar=Scrollbar(self,orient=VERTICAL)
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.vbar.config(command=self.canvas.yview)
        self.hbar=Scrollbar(self,orient=HORIZONTAL)
        self.hbar.grid(row=2, column=0, sticky="ew")
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        #zoom button
        save_button = Button(self, text = "Zoom")
        save_button["command"] = lambda: self.zoom_in()
        save_button.grid(row=3, column = 0, pady = 5)

    def zoom_in(self):
        #Clean canvas
        self.canvas.delete("all")
        self.size_x = int(self.size_x * 1.1)
        self.size_y = int(self.size_y * 1.1)
        x=self.size_x
        y=self.size_y
        fontSize=int(x/20)
        self.canvas.create_line(self.border, self.border, self.border, y-self.border)
        self.canvas.create_line(x-self.border, self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border, self.border, x-self.border, self.border)
        self.canvas.create_line(self.border, y-self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border,   self.border, x-self.border, y-self.border)
        text1=self.canvas.create_text(self.size_x/2, self.size_y/2, fill="white",font=("Purisa", fontSize) )
        self.canvas.itemconfig(text1, text="Graphic Text")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        #SCROLLING BARS
        self.vbar.config(command=self.canvas.yview)
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)


if __name__ == '__main__':
    my_gui=zoomer()
    my_gui.mainloop()
