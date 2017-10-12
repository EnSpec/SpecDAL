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
        # gui parts
        tk.Frame.__init__(self, parent)
        self.fig = plt.Figure(figsize=(6,6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        NavigationToolbar2TkAgg(self.canvas, self) # for matplotlib features
        self.canvas.get_tk_widget().pack(side=tk.LEFT)
        # data parts
        self.spectrum_mode = False
        self.collection = collection
        self.head = 0
        self.update(new_lim=True)
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
    def to_spectrum_mode(self):
        self.spectrum_mode = True
        self.update()
    def to_collection_mode(self):
        self.spectrum_mode = False
        self.update()
    def update(self, new_lim=False, plot_mask=False):
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
            spectrum.plot(ax=self.ax, label=spectrum.name)
            self.ax.legend()
        else:
            # red curves for masked spectra
            mask_style = ' '
            if plot_mask:
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
    path = '~/data/specdal/aidan_data2/ASD/'
    c = Collection("Test Collection", directory=path)
    for i in range(80):
        c.mask(c.spectra[i].name)
    root = tk.Tk()
    v = Viewer(root, c)
    v.update(plot_mask=True)
    root.mainloop()


if __name__ == "__main__":
    main()
