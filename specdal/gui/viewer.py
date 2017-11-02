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
import matplotlib
sys.path.insert(0, os.path.abspath("../.."))
from specdal.spectrum import Spectrum
from specdal.collection import Collection
matplotlib.use('TkAgg')

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
        NavigationToolbar2TkAgg(self.canvas, self) # for matplotlib features
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
        # spectra list
        self.scrollbar = ttk.Scrollbar(self)
        self.listbox = tk.Listbox(self, yscrollcommand=self.scrollbar.set,
                                  selectmode=tk.EXTENDED, width=30)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', lambda x: self.set_head(self.listbox.curselection()[0]))
        # toggle options
        self.mean = False
        self.median = False
        self.max = False
        self.min = False
        self.std = False
        self.spectrum_mode = False
        self.show_masked = True
        # data
        self.collection = collection
        self.head = 0
        self.mask_filepath = os.path.abspath('./masked_spectra.txt')
        if collection:
            self.update(new_lim=True)
            self.update_list()
        # pack
        self.pack()
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
        self.head = value
        if self.spectrum_mode:
            self.update()
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
    def create_toolbar(self):
        self.toolbar = tk.Frame(self)
        tk.Button(self.toolbar, text='Read', command=lambda:
                  self.read_dir()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Mode', command=lambda:
                  self.toggle_mode()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Show/Hide Masked',
                  command=lambda: self.toggle_show_masked()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Mask/Unmask', command=lambda:
                  self.toggle_mask()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Unmask all', command=lambda:
                  self.unmask_all()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Save Mask', command=lambda:
                  self.save_mask()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Save Mask As', command=lambda:
                  self.save_mask_as()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Stitch', command=lambda:
                  self.stitch()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Jump_Correct', command=lambda:
                  self.jump_correct()).pack(side=tk.LEFT)       
        tk.Button(self.toolbar, text='mean', command=lambda:
                  self.toggle_mean()).pack(side=tk.LEFT)       
        tk.Button(self.toolbar, text='median', command=lambda:
                  self.toggle_median()).pack(side=tk.LEFT)       
        tk.Button(self.toolbar, text='max', command=lambda:
                  self.toggle_max()).pack(side=tk.LEFT)       
        tk.Button(self.toolbar, text='min', command=lambda:
                  self.toggle_min()).pack(side=tk.LEFT)       
        tk.Button(self.toolbar, text='std', command=lambda:
                  self.toggle_std()).pack(side=tk.LEFT)       
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
    def set_collection(self, collection):
        new_lim = True if self.collection is None else False
        self.collection = collection
        self.update(new_lim=new_lim)
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
    def toggle_show_masked(self):
        if self.show_masked:
            self.show_masked = False
        else:
            self.show_masked = True
        self.update()
    def unmask_all(self):
        for spectrum in list(self.collection.masks):
            self.collection.unmask(spectrum)
        self.update()
        self.update_list()
    def toggle_mask(self):
        idx = self.listbox.curselection()
        for i in idx:
            spectrum = self.collection.spectra[i].name
            if spectrum in self.collection.masks:
                self.collection.unmask(spectrum)
                self.listbox.itemconfigure(i, foreground='black')
            else:
                self.collection.mask(spectrum)
                self.listbox.itemconfigure(i, foreground='red')
        # update figure
        self.update()
    def save_mask(self):
        ''' save mask to self.mask_filepath'''
        with open(self.mask_filepath, 'w') as f:
            for spectrum in self.collection.masks:
                print(spectrum, file=f)
    def save_mask_as(self):
        ''' modify self.mask_filepath and call save_mask()'''
        mask_filepath = filedialog.asksaveasfilename()
        if os.path.splitext(mask_filepath)[1] == '':
            mask_filepath = mask_filepath + '.txt'
        self.mask_filepath = mask_filepath
        self.save_mask()
    def update_list(self):
        self.listbox.delete(0, tk.END)
        for i, spectrum in enumerate(self.collection.spectra):
            self.listbox.insert(tk.END, spectrum.name)
            if spectrum.name in self.collection.masks:
                self.listbox.itemconfigure(i, foreground='red')
                
    def update(self, new_lim=False):
        """ Update the plot """
        if self.collection is None:
            return
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
            masks = [s.name in self.collection.masks for s in spectra]
            mask_style = ' '
            if self.show_masked:
                mask_style = 'r'
            Collection(name='selection',
                       spectra=spectra).plot(ax=self.ax,
                                             style=list(np.where(masks, mask_style, 'k')),
                                             picker=1)
            self.ax.set_title('selection')            
            # c = str(np.where(spectrum.name in self.collection.masks, 'r', 'k'))
            # spectrum.plot(ax=self.ax, label=spectrum.name, c=c)
        else:
            # red curves for masked spectra
            mask_style = ' '
            if self.show_masked:
                mask_style = 'r'
            masks = [s.name in self.collection.masks for s in self.collection.spectra]
            self.collection.plot(ax=self.ax,
                                 style=list(np.where(masks, mask_style, 'k')),
                                 picker=1)
            self.ax.set_title(self.collection.name)

        def onpick(event):
            spectrum_name = event.artist.get_label()
            pos = list(self.collection._spectra.keys()).index(spectrum_name)
            self.listbox.selection_set(pos)
        self.fig.canvas.mpl_connect('pick_event', onpick)

            
        if self.mean:
            self.collection.mean().plot(ax=self.ax, c='b', label=self.collection.name + '_mean')
        if self.median:
            self.collection.median().plot(ax=self.ax, c='g', label=self.collection.name + '_median')
        if self.max:
            self.collection.max().plot(ax=self.ax, c='y', label=self.collection.name + '_max')
        if self.min:
            self.collection.min().plot(ax=self.ax, c='m', label=self.collection.name + '_min')
        if self.std:
            self.collection.std().plot(ax=self.ax, c='c', label=self.collection.name + '_std')
        # reapply limits
        if new_lim == False:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        # legend
        if self.spectrum_mode:
            self.ax.legend()
        else:
            self.ax.legend().remove()
        self.ax.set_ylabel(self.collection.measure_type)
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
        self.update()
    def jump_correct(self):
        ''' 
        Known Bugs
        ----------
        Only performs jump correction on 1000 and 1800 wvls and 1 reference
        '''
        self.collection.jump_correct([1000, 1800], 1)
        self.update()
    def toggle_mean(self):
        if self.mean:
            self.mean = False
        else:
            self.mean = True
        self.update()
    def toggle_median(self):
        if self.median:
            self.median = False
        else:
            self.median = True
        self.update()
    def toggle_max(self):
        if self.max:
            self.max = False
        else:
            self.max = True
        self.update()
    def toggle_min(self):
        if self.min:
            self.min = False
        else:
            self.min = True
        self.update()
    def toggle_std(self):
        if self.std:
            self.std = False
        else:
            self.std = True
        self.update()

def read_test_data():
    path = '~/data/specdal/aidan_data2/ASD'
    c = Collection("Test Collection", directory=path)
    for i in range(30):
        c.mask(c.spectra[i].name)

def main():
    root = tk.Tk()
    v = Viewer(root, None)
    v.update()
    root.mainloop()


if __name__ == "__main__":
    main()
