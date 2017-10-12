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
    def __init__(self, parent, collection):
        tk.Frame.__init__(self, parent)
        # toolbar
        self.toolbar = tk.Frame(self)
        tk.Button(self.toolbar, text='Mode', command=lambda: self.toggle_mode()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Show/Hide Masked', command=lambda: self.toggle_show_masked()).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text='Mask/Unmask', command=lambda: self.toggle_mask()).pack(side=tk.LEFT)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        # canvas
        self.fig = plt.Figure(figsize=(6,6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        NavigationToolbar2TkAgg(self.canvas, self) # for matplotlib features
        self.canvas.get_tk_widget().pack(side=tk.LEFT)
        # spectra list
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox = tk.Listbox(self, yscrollcommand=self.scrollbar.set,
                                  width=30)
        self.scrollbar.config(command=self.listbox.yview)
        # self.listbox.bind('<Double-Button-1>', lambda x: self.set_head(self.listbox.curselection()[0]))
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.bind('<<ListboxSelect>>', lambda x: self.set_head(self.listbox.curselection()[0]))
        # data
        self.spectrum_mode = False
        self.show_masked = True
        self.collection = collection
        self.head = 0
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
    def toggle_mask(self):
        idx = self.listbox.curselection()[0]
        spectrum = self.collection.spectra[idx]
        if spectrum.name in self.collection.masks:
            self.collection.unmask(spectrum.name)
            self.listbox.itemconfigure(idx, foreground='black')
        else:
            self.collection.mask(spectrum.name)
            self.listbox.itemconfigure(idx, foreground='red')
        # update figure
        self.update()

    def update_list(self):
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
        if self.spectrum_mode:
            spectrum = self.collection.spectra[self.head]
            c = str(np.where(spectrum.name in self.collection.masks, 'r', 'k'))
            spectrum.plot(ax=self.ax, label=spectrum.name, c=c)
            self.ax.legend()
        else:
            # red curves for masked spectra
            mask_style = ' '
            if self.show_masked:
                mask_style = 'r'
            masks = [s.name in self.collection.masks for s in self.collection.spectra]
            self.collection.plot(ax=self.ax,
                                 style=list(np.where(masks, mask_style, 'k')))
            self.ax.legend().remove()
        # reapply limits
        if new_lim == False:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        self.ax.set_title(self.collection.name)
        self.ax.set_ylabel(self.collection.measure_type)
        self.canvas.draw()
    def next_spectrum(self):
        if not self.spectrum_mode:
            return
        self.head = (self.head + 1) % len(self.collection)
        self.update()

def main():
    path = '~/data/specdal/aidan_data2/SVC'
    c = Collection("Test Collection", directory=path)
    for i in range(30):
        c.mask(c.spectra[i].name)
    root = tk.Tk()
    v = Viewer(root, c)
    v.update()
    root.mainloop()


if __name__ == "__main__":
    main()
