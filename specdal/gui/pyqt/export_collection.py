import os
from matplotlib import pyplot as plt
from PyQt5 import QtCore

class CollectionExporter(QtCore.QThread):
    def export(self,collection,configuration):
        self.collection = collection
        self.configuration = configuration
        self.start()

    def run(self):
        c = self.collection
        configuration = self.configuration
        if not configuration['flags']:
            c = c.as_unflagged()
        # output individual spectra
        outdir = configuration['path']
        datadir = os.path.join(outdir, 'data')
        figdir = os.path.join(outdir, 'figures')
        os.makedirs(datadir,exist_ok=True)
        os.makedirs(figdir,exist_ok=True)
        if configuration['data']['individual']:
            indiv_datadir = os.path.join(datadir, 'indiv')
            os.makedirs(indiv_datadir,exist_ok=True)
            for spectrum in c.spectra:
                spectrum.to_csv(os.path.join(indiv_datadir, spectrum.name + '.csv'))

        if configuration['figures']['individual']:
            indiv_figdir = os.path.join(figdir, 'indiv')
            os.makedirs(indiv_figdir,exist_ok=True)
            for spectrum in c.spectra:
                spectrum.plot(legend=False)
                plt.savefig(os.path.join(indiv_figdir, spectrum.name + '.png'), bbox_inches='tight')
                plt.close()

        # output whole and group data
        if configuration['data']['dataset']:
            c.to_csv(os.path.join(datadir, c.name + ".csv"))

        if configuration['figures']['dataset']:
        # output whole and group figures (possibly with aggregates appended)
            c.plot(legend=False)
            plt.savefig(os.path.join(figdir, c.name + ".png"),  bbox_inches="tight")
            plt.close()

