import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
sys.path.insert(0, os.path.abspath("../.."))
from specdal.containers.spectrum import Spectrum
from collections import Iterable
from specdal.containers.collection import Collection
from datetime import datetime


class ToolBar(NavigationToolbar2Tk):
    def __init__(self,canvas_,parent,ax):
        NavigationToolbar2Tk.__init__(self,canvas_,parent)
        self._xlim = (0,1)
        self._ylim = (0,1)
        self._ax = ax
        self._canvas_ = canvas_

    def home(self):
        """Override home method to return to home of most recent plot"""
        self._ax.set_xlim(*self._xlim)
        self._ax.set_ylim(*self._ylim)
        self._canvas_.draw()

    def setHome(self,xlim,ylim):
        self._xlim = xlim
        self._ylim = ylim

class PlotConfigDialog(tk.Toplevel):

    def __init__(self, parent, xlim=(0,1),ylim=(0,1),title='',
            xlabel='',ylabel=''):
        tk.Toplevel.__init__(self,parent)
        self.transient(parent)
        self.parent = parent
        self.result = None
        self.title("Plot Config")
        self.xlim=xlim
        self.ylim=ylim
        self.title_ = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.applied = False

        body = tk.Frame(self)
        self.body(body)
        body.pack(fill=tk.BOTH,expand=1)
        
        btnFrame = tk.Frame(self)
        btnFrame.pack(side=tk.BOTTOM,fill=tk.X)
        tk.Button(btnFrame,text="OK",width=10,command=self.apply
                ).pack(side=tk.LEFT)
        tk.Button(btnFrame,text="Cancel",width=10,command=self.cancel
                ).pack(side=tk.LEFT)
    
        self.bind('<Return>',self.apply)
        self.bind('<Escape>',self.cancel)

        self.wait_window(self)

    def body(self,master):
        tk.Label(master,text="Plot Title: ").grid(sticky=tk.W,row=0)
        tk.Label(master,text="X-Label: ").grid(sticky=tk.W,row=1)
        tk.Label(master,text="Y-Label: ").grid(sticky=tk.W,row=2)
        tk.Label(master,text="X-Min: ").grid(sticky=tk.W,row=3)
        tk.Label(master,text="X-Max: ").grid(sticky=tk.W,row=4)
        tk.Label(master,text="Y-Min: ").grid(sticky=tk.W,row=5)
        tk.Label(master,text="Y-Max: ").grid(sticky=tk.W,row=6)

        self.titlebox = tk.Entry(master)
        self.titlebox.grid(sticky=tk.W+tk.E,row=0,column=1)
        self.titlebox.insert(0,self.title_)

        self.xlabelbox = tk.Entry(master)
        self.xlabelbox.grid(sticky=tk.W+tk.E,row=1,column=1)
        self.xlabelbox.insert(0,self.xlabel)

        self.ylabelbox = tk.Entry(master)
        self.ylabelbox.grid(sticky=tk.W+tk.E,row=2,column=1)
        self.ylabelbox.insert(0,self.ylabel)

        self.xminbox = tk.Entry(master)
        self.xminbox.grid(sticky=tk.W+tk.E,row=3,column=1)
        self.xminbox.insert(0,self.xlim[0])

        self.xmaxbox = tk.Entry(master)
        self.xmaxbox.grid(sticky=tk.W+tk.E,row=4,column=1)
        self.xmaxbox.insert(0,self.xlim[1])

        self.yminbox = tk.Entry(master)
        self.yminbox.grid(sticky=tk.W+tk.E,row=5,column=1)
        self.yminbox.insert(0,self.ylim[0])

        self.ymaxbox = tk.Entry(master)
        self.ymaxbox.grid(sticky=tk.W+tk.E,row=6,column=1)
        self.ymaxbox.insert(0,self.ylim[1])

    def apply(self,event=None):
        self.applied = True
        self.title = self.titlebox.get()   or ''
        self.xlabel = self.xlabelbox.get() or ''
        self.ylabel = self.ylabelbox.get() or ''
        self.xlim=float(self.xminbox.get())or 0,float(self.xmaxbox.get()) or 1
        self.ylim=float(self.yminbox.get())or 0,float(self.ymaxbox.get())or 1
        
        self.cancel()

    def cancel(self,event=None):
        self.parent.focus_set()
        self.destroy()


class ColorPickerDialog(tk.Toplevel):
    TOPLEVEL_COLORS = [(255,0,0),(255,165,0),(255,255,0),(0,255,0),
            (0,128,0),(0,0,255),(0,0,128),(128,0,128),(128,128,128)]
    
    FACTORS = [.55,.45,.35,.25,0,.95,.75,.55,.35,.15]
    GS_FACTORS = [1,.8,.5,.2,0,.9,.7,.5,.2,0]
    def __init__(self, parent, start_color=(0,0,0)):
        tk.Toplevel.__init__(self,parent)
        self.transient(parent)
        self.parent = parent
        self.result = None
        self.title("Color Picker")
        self.applied = False

        body = tk.Frame(self)
        self.body(body)
        body.pack(fill=tk.BOTH,expand=1)
        
        self.bind('<Escape>',self.cancel)

        self.wait_window(self)

    def apply(self,color=None):
        print(color)
        self.applied = True
        self.color = color
        self.cancel()

    def cancel(self,event=None):
        self.parent.focus_set()
        self.destroy()

    def tint(self,color,factor):
        r = color[0]+(255-color[0])*factor
        g = color[1]+(255-color[1])*factor
        b = color[2]+(255-color[2])*factor
        return (r,g,b)

    def shade(self,color,factor):
        r = color[0]*factor
        g = color[1]*factor
        b = color[2]*factor
        return r,g,b

    def toHex(self,color):
        out = ["#"]
        for c in color:
           out.append(('%2s'%hex(int(c))[2:]).replace(' ','0'))
        return ''.join(out)


    def body(self,master):
        for i,color in enumerate(self.TOPLEVEL_COLORS):
            factors = self.FACTORS if i < len(self.TOPLEVEL_COLORS)-1 \
                    else self.GS_FACTORS
            for j in range(10):
                if j < 5:
                    c = self.toHex(self.tint(color,factors[j]))
                else:
                    c = self.toHex(self.shade(color,factors[j]))
                frame = tk.Frame(master,bg=c,width="24",height="24",
                        #activebackground=cpehighlightbackground=c,
                        borderwidth=0,
                        #command=
                        )
                frame.bind("<Button-1>",lambda event,c=c:self.apply(color=c))
                frame.grid(row=j+1,column=i+1)

class Viewer(tk.Frame):
    def __init__(self, parent, collection=None, with_toolbar=True):
        tk.Frame.__init__(self, parent)
        # toolbar
        if with_toolbar:
            self.create_toolbar()

        # canvas
        #canvas_frame = tk.Frame(self)
        #canvas_frame.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        #title_frame = tk.Frame(canvas_frame)
        #title_frame.pack(side=tk.TOP,anchor=tk.NW)
        #tk.Label(title_frame,text=" Plot Title: ").pack(side=tk.LEFT)
        #self._title = tk.Entry(title_frame,width=30)
        #self._title.pack(side=tk.LEFT)
        #tk.Button(title_frame, text='Set', command=lambda: self.updateTitle()
        #        ).pack(side=tk.LEFT)

        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.setupMouseNavigation()
        self.navbar = ToolBar(self.canvas, self, self.ax) # for matplotlib features
        self.setupNavBarExtras(self.navbar)
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH,expand=1)
        # spectra list
        self.create_listbox()
        # toggle options
        self.mean = False
        self.median = False
        self.max = False
        self.min = False
        self.std = False

        
        self.spectrum_mode = False
        self.show_flagged = True
        # data
        self.collection = collection
        self.head = 0
        self.flag_filepath = os.path.abspath('./flagged_spectra.txt')
        if collection:
            self.update_artists(new_lim=True)
            self.update_list()


        # pack
        self.pack(fill=tk.BOTH,expand=1)
        self.color = '#000000'


    def returnToSelectMode(self):
        if self.ax.get_navigate_mode() == 'PAN':
            #Turn panning off
            self.navbar.pan()
        elif self.ax.get_navigate_mode() == 'ZOOM':
            #Turn zooming off
            self.navbar.zoom()

    def setupNavBarExtras(self,navbar):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        self.select_icon = tk.PhotoImage(file=os.path.join(working_dir,"select.png"))

        self.select_button = tk.Button(navbar,width="24",height="24",
                image=self.select_icon, command = self.returnToSelectMode).pack(side=tk.LEFT,anchor=tk.W)

        self.dirLbl = tk.Label(navbar,text="Viewing: None")
        self.dirLbl.pack(side=tk.LEFT,anchor=tk.W)

    
    def plotConfig(self):
        config = PlotConfigDialog(self,title=self.ax.get_title(),
                xlabel=self.ax.get_xlabel(),ylabel=self.ax.get_ylabel(),
                xlim=self.ax.get_xlim(),ylim=self.ax.get_ylim()
        )
        if(config.applied):
            print(config.title)
            print(config.xlim)
            self.ax.set_title(config.title)
            self.ax.set_xlabel(config.xlabel)
            self.ax.set_ylabel(config.ylabel)
            self.ax.set_xlim(*config.xlim)
            self.ax.set_ylim(*config.ylim)
            self.canvas.draw()

    def rectangleStartEvent(self,event):
        self._rect = None
        self._rect_start = event

    def rectangleMoveEvent(self,event):
        try:
            dx = event.xdata - self._rect_start.xdata
            dy = event.ydata - self._rect_start.ydata
        except TypeError:
            #we're out of canvas bounds
            return

        if self._rect is not None:
            self._rect.remove()

        self._rect = Rectangle((self._rect_start.xdata,self._rect_start.ydata),
                dx,dy, color='k',ls='--',lw=1,fill=False)
        self.ax.add_patch(self._rect)
        self.ax.draw_artist(self._rect)

    def rectangleEndEvent(self,event):
        if self._rect is not None:
            self._rect.remove()
        else:
            #make a small, fake rectangle
            class FakeEvent(object):
                def __init__(self,x,y):
                    self.xdata, self.ydata = x, y

            dy = (self.ax.get_ylim()[1]-self.ax.get_ylim()[0])/100.
            self._rect_start = FakeEvent(event.xdata-10,event.ydata+dy)
            event = FakeEvent(event.xdata+10,event.ydata-dy)

        if not self.collection is None:
            x0 = min(self._rect_start.xdata,event.xdata)
            x1 = max(self._rect_start.xdata,event.xdata)
            y0 = min(self._rect_start.ydata,event.ydata)
            y1 = max(self._rect_start.ydata,event.ydata)
            try:
                #if our data is sorted, we can easily isolate it
                x_data = self.collection.data.loc[x0:x1]
            except:
                #Pandas builtin throws an error, use another pandas builtin
                data = self.collection.data
                in_xrange = (data.index >= x0) & (data.index <= x1)
                x_data = data.iloc[in_xrange]

            ylim = sorted([self._rect_start.ydata,event.ydata])
            is_in_box = ((x_data > y0) & (x_data < y1)).any()
            
            highlighted = is_in_box.index[is_in_box].tolist()
            key_list = list(self.collection._spectra.keys())

            self.update_selected(highlighted)
            flags = self.collection.flags
            for highlight in highlighted:
                #O(n^2) woof
                if (not (highlight in flags)) or self.show_flagged:
                    pos = key_list.index(highlight)
                    self.listbox.selection_set(pos)

    
    def setupMouseNavigation(self):
        self.clicked = False
        self.select_mode = 'rectangle'
        self._bg_cache = None
        
        START_EVENTS = {
            'rectangle':self.rectangleStartEvent
        }

        MOVE_EVENTS = {
            'rectangle':self.rectangleMoveEvent
        }

        END_EVENTS = {
            'rectangle':self.rectangleEndEvent
        }

        def onMouseDown(event):
            if self.ax.get_navigate_mode() is None:
                self._bg_cache = self.canvas.copy_from_bbox(self.ax.bbox)
                self.clicked = True
                START_EVENTS[self.select_mode](event)

        def onMouseUp(event):
            if self.ax.get_navigate_mode() is None:
                self.canvas.restore_region(self._bg_cache)
                self.canvas.blit(self.ax.bbox)
                self.clicked = False
                END_EVENTS[self.select_mode](event)

        def onMouseMove(event):
            if self.ax.get_navigate_mode() is None:
                if(self.clicked):
                    self.canvas.restore_region(self._bg_cache)
                    MOVE_EVENTS[self.select_mode](event)
                    self.canvas.blit(self.ax.bbox)

        self.canvas.mpl_connect('button_press_event',onMouseDown)
        self.canvas.mpl_connect('button_release_event',onMouseUp)
        self.canvas.mpl_connect('motion_notify_event',onMouseMove)

        

    @property
    def head(self):
        return self._head
    @head.setter
    def head(self, value):
        if not hasattr(self, '_head'):
            self._head = 0
        else:
            self._head = value % len(self.collection)
    def set_head(self, value):
        if isinstance(value, Iterable):
            if len(value) > 0:
                value = value[0]
            else:
                value = 0
        self.head = value
        if self.spectrum_mode:
            self.update()
        self.update_selected()

    @property
    def collection(self):
        return self._collection
    @collection.setter
    def collection(self, value):
        if isinstance(value, Spectrum):
            # create new collection
            self._collection = Collection(name=Spectrum.name, spectra=[value])
        if isinstance(value, Collection):
            self._collection = value
        else:
            self._collection = None


    def move_selected_to_top(self):
        selected = self.listbox.curselection()
        keys = [self.collection.spectra[s].name for s in selected]
        for s in selected[::-1]:
            self.listbox.delete(s)
        self.listbox.insert(0,*keys)
        self.listbox.selection_set(0,len(keys))

    def unselect_all(self):
        self.listbox.selection_clear(0,tk.END)
        self.update_selected()

    def select_all(self):
        self.listbox.selection_set(0,tk.END)
        self.update_selected()

    def invert_selection(self):
        for i in range(self.listbox.size()):
            if self.listbox.selection_includes(i):
                self.listbox.selection_clear(i)
            else:
                self.listbox.selection_set(i)
        self.update_selected()

    def change_color(self):
        cpicker = ColorPickerDialog(self)
        #rgb,color = askcolor(self.color)
        if cpicker.applied:
            self.color = cpicker.color 
            self.color_pick.config(bg=self.color)
            #update our list of chosen colors
            selected = self.listbox.curselection()
            selected_keys = [self.collection.spectra[s].name for s in selected]

            for key in selected_keys:
                self.colors[key] = self.color
            self.update()

    def select_by_name(self):
        pattern = self.name_filter.get()
        for i in range(self.listbox.size()):
            if pattern in self.listbox.get(i):
                self.listbox.selection_set(i)
            else:
                self.listbox.selection_clear(i)
        self.update_selected()


    def create_listbox(self):
        self._sbframe = tk.Frame(self)

        list_label = tk.Frame(self._sbframe)
        list_label.pack(side=tk.TOP,anchor=tk.N,fill=tk.X)
        tk.Label(list_label,text="Name:").pack(side=tk.LEFT,anchor=tk.W)
        self.name_filter = tk.Entry(list_label,width=14)
        self.name_filter.pack(side=tk.LEFT,anchor=tk.W)
        tk.Button(list_label,text="Select",
                command=lambda:self.select_by_name()).pack(side=tk.LEFT,anchor=tk.W)
        self.sblabel = tk.Label(list_label,text="Showing: 0")
        self.sblabel.pack(side=tk.RIGHT)

        self.scrollbar = tk.Scrollbar(self._sbframe)
        self.listbox = tk.Listbox(self._sbframe, yscrollcommand=self.scrollbar.set,
                                  selectmode=tk.EXTENDED, width=30)
        self.scrollbar.config(command=self.listbox.yview)

        self.list_tools = tk.Frame(self._sbframe)
        tk.Button(self.list_tools, text="To Top", command = lambda:self.move_selected_to_top()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        tk.Button(self.list_tools, text="Select All", command = lambda:self.select_all()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        tk.Button(self.list_tools, text="Clear", command = lambda:self.unselect_all()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        tk.Button(self.list_tools, text="Invert", command = lambda:self.invert_selection()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)

        self.color_field=tk.Frame(self.list_tools)
        tk.Label(self.color_field, text="Color:").pack(side=tk.LEFT)

        self.color_pick = tk.Button(self.color_field, text="",
                command=lambda:self.change_color(), bg='#000000')
        self.color_pick.pack(side=tk.RIGHT,anchor=tk.NW,fill=tk.X,expand=True)

        self.color_field.pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)

        self.list_tools.pack(side=tk.RIGHT,anchor=tk.NW)
        self.scrollbar.pack(side=tk.RIGHT,anchor=tk.E, fill=tk.Y)
        self.listbox.pack(side=tk.RIGHT,anchor=tk.E, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', lambda x: 
                self.set_head(self.listbox.curselection()))
        self._sbframe.pack(side=tk.RIGHT,anchor=tk.E,fill=tk.Y)

    def create_toolbar(self):
        self.toolbar = tk.Frame(self)
        tk.Button(self.toolbar, text='Read', command=lambda:
                  self.read_dir()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Mode', command=lambda:
                  self.toggle_mode()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text="Plot Config", command=lambda:
                  self.plotConfig()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Show/Hide Flagged',
                  command=lambda: self.toggle_show_flagged()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Flag/Unflag', command=lambda:
                  self.toggle_flag()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Unflag all', command=lambda:
                  self.unflag_all()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        #tk.Button(self.toolbar, text='Save Flag', command=lambda:
        #          self.save_flag()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Save Flags', command=lambda:
                  self.save_flag_as()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Stitch', command=lambda:
                  self.stitch()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Jump_Correct', command=lambda:
                  self.jump_correct()).pack(side=tk.LEFT,fill=tk.X,expand=1)       
        tk.Button(self.toolbar, text='mean', command=lambda:
                  self.toggle_mean()).pack(side=tk.LEFT,fill=tk.X,expand=1)       
        tk.Button(self.toolbar, text='median', command=lambda:
                  self.toggle_median()).pack(side=tk.LEFT,fill=tk.X,expand=1)       
        tk.Button(self.toolbar, text='max', command=lambda:
                  self.toggle_max()).pack(side=tk.LEFT,fill=tk.X,expand=1)       
        tk.Button(self.toolbar, text='min', command=lambda:
                  self.toggle_min()).pack(side=tk.LEFT,fill=tk.X,expand=1)       
        tk.Button(self.toolbar, text='std', command=lambda:
                  self.toggle_std()).pack(side=tk.LEFT,fill=tk.X,expand=1)       
        self.toolbar.pack(side=tk.TOP, fill=tk.X)




    def updateTitle(self):
        print("Hello world!")
        self.ax.set_title(self._title.get())
        self.canvas.draw()

    def set_collection(self, collection):
        new_lim = True if self.collection is None else False
        self.collection = collection
        self.update_artists(new_lim=new_lim)
        self.update()
        self.update_list()

    def read_dir(self):
        try:
            directory = os.path.split(filedialog.askopenfilename(
               filetypes=(
                   ("Supported types","*.asd *.sed *.sig *.pico"),
                   ("All files","*"),
                   )
            ))[0]
        except:
            return
        if not directory:
            return
        c = Collection(name="collection", directory=directory)
        self.set_collection(c)
        self.dirLbl.config(text="Viewing: "+directory)

    def reset_stats(self):
        if self.mean_line:
            self.mean_line.remove()
            self.mean_line = None
            self.mean = False
        if self.median_line:
            self.median_line.remove()
            self.median_line = None
            self.median = False
        if self.max_line:
            self.max_line.remove()
            self.max_line = None
            self.max = False
        if self.min_line:
            self.min_line.remove()
            self.min_line = None
            self.min = False
        if self.std_line:
            self.std_line.remove()
            self.std_line = None
            self.std = False

    def toggle_mode(self):
        if self.spectrum_mode:
            self.spectrum_mode = False
        else:
            self.spectrum_mode = True
        self.update()
    def toggle_show_flagged(self):
        if self.show_flagged:
            self.show_flagged = False
        else:
            self.show_flagged = True
        self.update()
    def unflag_all(self):
        #new flags -> new statistics
        self.reset_stats()

        for spectrum in list(self.collection.flags):
            self.collection.unflag(spectrum)
        self.update()
        self.update_list()

    def toggle_flag(self):
        #new flags -> new statistics
        self.reset_stats()

        selected = self.listbox.curselection()
        keys = [self.listbox.get(s) for s in selected]
        
        for i,key in enumerate(keys):
            print(i,key)
            spectrum = key
            if spectrum in self.collection.flags:
                self.collection.unflag(spectrum)
                self.listbox.itemconfigure(selected[i], foreground='black')
            else:
                self.collection.flag(spectrum)
                self.listbox.itemconfigure(selected[i], foreground='red')
        # update figure
        self.update()
    def save_flag(self):
        ''' save flag to self.flag_filepath'''
        with open(self.flag_filepath, 'w') as f:
            for spectrum in self.collection.flags:
                print(spectrum, file=f)
    def save_flag_as(self):
        ''' modify self.flag_filepath and call save_flag()'''
        flag_filepath = filedialog.asksaveasfilename()
        if os.path.splitext(flag_filepath)[1] == '':
            flag_filepath = flag_filepath + '.txt'
        self.flag_filepath = flag_filepath
        self.save_flag()

    def update_list(self):
        self.listbox.delete(0, tk.END)
        for i, spectrum in enumerate(self.collection.spectra):
            self.listbox.insert(tk.END, spectrum.name)
            if spectrum.name in self.collection.flags:
                self.listbox.itemconfigure(i, foreground='red')
        self.update_selected()
    
    def ask_for_draw(self):
        #debounce canvas updates
        now = datetime.now()
        print(now-self.last_draw)
        if((now-self.last_draw).total_seconds() > 0.5):
            self.canvas.draw()
            self.last_draw = now

    def update_artists(self,new_lim=False):
        if self.collection is None:
            return
        #update values being plotted -> redo statistics
        self.mean_line = None
        self.median_line = None
        self.max_line = None
        self.min_line = None
        self.std_line = None
        # save limits
        if new_lim == False:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
        # plot
        self.ax.clear()
        # show statistics
        if self.spectrum_mode:
            idx = self.listbox.curselection()
            if len(idx) == 0:
                idx = [self.head]
            spectra = [self.collection.spectra[i] for i in idx]
            flags = [s.name in self.collection.flags for s in spectra]
            print("flags = ", flags)
            flag_style = ' '
            if self.show_flagged:
                flag_style = 'r'
            artists = Collection(name='selection', spectra=spectra).plot(ax=self.ax,
                         style=list(np.where(flags, flag_style, self.color)),
                         picker=1)
            self.ax.set_title('selection')            
            # c = str(np.where(spectrum.name in self.collection.flags, 'r', 'k'))
            # spectrum.plot(ax=self.ax, label=spectrum.name, c=c)
        else:
            # red curves for flagged spectra
            flag_style = ' '
            if self.show_flagged:
                flag_style = 'r'
            flags = [s.name in self.collection.flags for s in self.collection.spectra]
            print("flags = ", flags)
            self.collection.plot(ax=self.ax,
                                 style=list(np.where(flags, flag_style, 'k')),
                                 picker=1)
            #self.ax.set_title(self.collection.name)

        keys = [s.name for s in self.collection.spectra]
        artists = self.ax.lines
        self.artist_dict = {key:artist for key,artist in zip(keys,artists)}
        self.colors = {key:'black' for key in keys}
        self.ax.legend().remove()
        self.navbar.setHome(self.ax.get_xlim(),self.ax.get_ylim())
        self.canvas.draw()
        self.sblabel.config(text="Showing: {}".format(len(artists)))

    def update_selected(self,to_add=None):
        """ Update, only on flaged"""
        if self.collection is None:
            return

        if to_add:
            for key in to_add:
                self.artist_dict[key].set_linestyle('--')
        else:
            keys = [s.name for s in self.collection.spectra]
            selected = self.listbox.curselection()
            selected_keys = [self.collection.spectra[s].name for s in selected]
            for key in keys:
                if key in selected_keys:
                    self.artist_dict[key].set_linestyle('--')
                else:
                    self.artist_dict[key].set_linestyle('-')
        self.canvas.draw()


    def update(self):
        """ Update the plot """
        if self.collection is None:
            return
        # show statistics
        if self.spectrum_mode:
            self.ax.clear()
            idx = self.listbox.curselection()
            if len(idx) == 0:
                idx = [self.head]
            spectra = [self.collection.spectra[i] for i in idx]
            flags = [s.name in self.collection.flags for s in spectra]
            print("flags = ", flags)
            flag_style = ' '
            if self.show_flagged:
                flag_style = 'r'
            Collection(name='selection',
                       spectra=spectra).plot(ax=self.ax,
                                             style=list(np.where(flags, flag_style, 'k')),
                                             picker=1)
            self.ax.set_title('selection')            
            # c = str(np.where(spectrum.name in self.collection.flags, 'r', 'k'))
            # spectrum.plot(ax=self.ax, label=spectrum.name, c=c)
        else:
            # red curves for flagged spectra

            keys = [s.name for s in self.collection.spectra]
            for key in keys:
                if key in self.collection.flags:
                    if self.show_flagged:
                        self.artist_dict[key].set_visible(True)
                        self.artist_dict[key].set_color('red')
                    else:
                        self.artist_dict[key].set_visible(False)
                else:
                    self.artist_dict[key].set_color(self.colors[key])
                    self.artist_dict[key].set_visible(True)

            if self.show_flagged:
                self.sblabel.config(text="Showing: {}".format(len(self.artist_dict)))
            else:
                self.sblabel.config(text="Showing: {}".format(
                    len(self.artist_dict)-len(self.collection.flags)))
            '''
            self.collection.plot(ax=self.ax,
                                 style=list(np.where(flags, flag_style, 'k')),
                                 picker=1)
            self.ax.set_title(self.collection.name)
            '''
            
        if self.spectrum_mode:
            #self.ax.legend()
            pass
        else:
            #self.ax.legend().remove()
            pass
        self.ax.set_ylabel(self.collection.measure_type)
        #toggle appearance of statistics
        if self.mean_line != None: self.mean_line.set_visible(self.mean)
        if self.median_line != None: self.median_line.set_visible(self.median)
        if self.max_line != None: self.max_line.set_visible(self.max)
        if self.min_line != None: self.min_line.set_visible(self.min)
        if self.std_line != None: self.std_line.set_visible(self.std)
        self.canvas.draw()

    def next_spectrum(self):
        if not self.spectrum_mode:
            return
        self.head = (self.head + 1) % len(self.collection)
        self.update()
    def stitch(self):
        ''' 
        Known Bugs
        ----------
        Can't stitch one spectrum and plot the collection
        '''
        self.collection.stitch()
        self.update_artists()

    def jump_correct(self):
        ''' 
        Known Bugs
        ----------
        Only performs jump correction on 1000 and 1800 wvls and 1 reference
        '''
        self.collection.jump_correct([1000, 1800], 1)
        self.update_artists()

    def toggle_mean(self):
        if self.mean:
            self.mean = False

        else:
            self.mean = True
            if not self.mean_line:
                self.collection.mean().plot(ax=self.ax, c='b', label=self.collection.name + '_mean',lw=3)
                self.mean_line = self.ax.lines[-1]
        self.update()

    def toggle_median(self):
        if self.median:
            self.median = False
        else:
            self.median = True
            if not self.median_line:
                self.collection.median().plot(ax=self.ax, c='g', label=self.collection.name + '_median',lw=3)
                self.median_line = self.ax.lines[-1]
        self.update()
    def toggle_max(self):
        if self.max:
            self.max = False
        else:
            self.max = True
            if not self.max_line:
                self.collection.max().plot(ax=self.ax, c='y', label=self.collection.name + '_max',lw=3)
                self.max_line = self.ax.lines[-1]
        self.update()
    def toggle_min(self):
        if self.min:
            self.min = False
        else:
            self.min = True
            if not self.min_line:
                self.collection.min().plot(ax=self.ax, c='m', label=self.collection.name + '_min',lw=3)
                self.min_line = self.ax.lines[-1]
        self.update()

    def toggle_std(self):
        if self.std:
            self.std = False
        else:
            self.std = True
            if not self.std_line:
                self.collection.std().plot(ax=self.ax, c='c', label=self.collection.name + '_std',lw=3)
                self.std_line = self.ax.lines[-1]
        self.update()

def read_test_data():
    path = '~/data/specdal/aidan_data2/ASD'
    c = Collection("Test Collection", directory=path)
    for i in range(30):
        c.flag(c.spectra[i].name)

def main():
    root = tk.Tk()
    v = Viewer(root, None)
    v.update()
    root.mainloop()

if __name__ == "__main__":
    main()
