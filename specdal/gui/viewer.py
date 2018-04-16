import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib
sys.path.insert(0, os.path.abspath("../.."))
from specdal.containers.spectrum import Spectrum
from collections import Iterable
from specdal.containers.collection import Collection
matplotlib.use('TkAgg')
from datetime import datetime

class Viewer(tk.Frame):
    def __init__(self, parent, collection=None, with_toolbar=True):
        tk.Frame.__init__(self, parent)
        # toolbar
        if with_toolbar:
            self.create_toolbar()
        # canvas
        self.fig = plt.Figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.setupMouseNavigation()
        self.navbar = NavigationToolbar2TkAgg(self.canvas, self) # for matplotlib features
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
        self.last_draw = datetime.now()


    def setupNavBarExtras(self,navbar):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        self.select_icon = tk.PhotoImage(file=os.path.join(working_dir,"select.png"))

        self.select_button = tk.Button(navbar,width="24",height="24",
                image=self.select_icon, command = lambda:self.ax.set_navigate_mode(None)).pack(side=tk.LEFT,anchor=tk.W)



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

        if not self.collection is None:
            x_data = self.collection.data.loc[self._rect_start.xdata:event.xdata]
            ylim = sorted([self._rect_start.ydata,event.ydata])
            is_in_box = ((x_data > ylim[0]) & (x_data < ylim[1])).any()
            
            highlighted = is_in_box.index[is_in_box].tolist()
            key_list = list(self.collection._spectra.keys())

            self.update_selected(highlighted)
            for highlight in highlighted:
                #O(n^2) woof
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
            self.canvas.restore_region(self._bg_cache)
            self.canvas.blit(self.ax.bbox)
            self.clicked = False
            END_EVENTS[self.select_mode](event)

        def onMouseMove(event):
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

    def create_listbox(self):
        self.scrollbar = ttk.Scrollbar(self)
        self.listbox = tk.Listbox(self, yscrollcommand=self.scrollbar.set,
                                  selectmode=tk.EXTENDED, width=30)
        self.scrollbar.config(command=self.listbox.yview)

        self.list_tools = tk.Frame(self)
        tk.Button(self.list_tools, text="To Top", command = lambda:self.move_selected_to_top()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        tk.Button(self.list_tools, text="Select All", command = lambda:self.select_all()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        tk.Button(self.list_tools, text="Clear", command = lambda:self.unselect_all()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        tk.Button(self.list_tools, text="Invert", command = lambda:self.invert_selection()
                ).pack(side=tk.TOP,anchor=tk.NW,fill=tk.X)
        self.list_tools.pack(side=tk.RIGHT,anchor=tk.NW)
        self.scrollbar.pack(side=tk.RIGHT,anchor=tk.E, fill=tk.Y)
        self.listbox.pack(side=tk.RIGHT,anchor=tk.E, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', lambda x: 
                self.set_head(self.listbox.curselection()))

    def create_toolbar(self):
        self.toolbar = tk.Frame(self)
        tk.Button(self.toolbar, text='Read', command=lambda:
                  self.read_dir()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Mode', command=lambda:
                  self.toggle_mode()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Show/Hide Flagged',
                  command=lambda: self.toggle_show_flagged()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Flag/Unflag', command=lambda:
                  self.toggle_flag()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Unflag all', command=lambda:
                  self.unflag_all()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Save Flag', command=lambda:
                  self.save_flag()).pack(side=tk.LEFT,fill=tk.X,expand=1)
        tk.Button(self.toolbar, text='Save Flag As', command=lambda:
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

    def set_collection(self, collection):
        new_lim = True if self.collection is None else False
        self.collection = collection
        self.update_artists(new_lim=new_lim)
        self.update()
        self.update_list()

    def read_dir(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        c = Collection(name="collection", directory=directory)
        self.set_collection(c)
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
        for spectrum in list(self.collection.flags):
            self.collection.unflag(spectrum)
        self.update()
        self.update_list()

    def toggle_flag(self):
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
                         style=list(np.where(flags, flag_style, 'k')),
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
            self.ax.set_title(self.collection.name)

        keys = [s.name for s in self.collection.spectra]
        artists = self.ax.lines
        self.artist_dict = {key:artist for key,artist in zip(keys,artists)}
        self.canvas.draw()

        '''
        def onpick(event):
            spectrum_name = event.artist.get_label()
            pos = list(self.collection._spectra.keys()).index(spectrum_name)
            self.listbox.selection_set(pos)
        self.fig.canvas.mpl_connect('pick_event', onpick)
        '''

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
                    self.artist_dict[key].set_color('black')

            '''
            self.collection.plot(ax=self.ax,
                                 style=list(np.where(flags, flag_style, 'k')),
                                 picker=1)
            self.ax.set_title(self.collection.name)
            '''
            
        # reapply limits
        # legend
        self.ax.legend().remove()
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
                self.collection.mean().plot(ax=self.ax, c='b', label=self.collection.name + '_mean')
                self.mean_line = self.ax.lines[-1]
        self.update()

    def toggle_median(self):
        if self.median:
            self.median = False
        else:
            self.median = True
            if not self.median_line:
                self.collection.median().plot(ax=self.ax, c='g', label=self.collection.name + '_median')
                self.median_line = self.ax.lines[-1]
        self.update()
    def toggle_max(self):
        if self.max:
            self.max = False
        else:
            self.max = True
            if not self.max_line:
                self.collection.max().plot(ax=self.ax, c='y', label=self.collection.name + '_max')
                self.max_line = self.ax.lines[-1]
        self.update()
    def toggle_min(self):
        if self.min:
            self.min = False
        else:
            self.min = True
            if not self.min_line:
                self.collection.min().plot(ax=self.ax, c='m', label=self.collection.name + '_min')
                self.min_line = self.ax.lines[-1]
        self.update()

    def toggle_std(self):
        if self.std:
            self.std = False
        else:
            self.std = True
            if not self.std_line:
                self.collection.std().plot(ax=self.ax, c='c', label=self.collection.name + '_std')
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
