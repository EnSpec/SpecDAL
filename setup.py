from distutils.core import setup

setup(name='specdal',
      version='0.2.2',
      description='Package for processing spectroscopy data',
      long_description=open('README.rst').read(),
      scripts=[
          'bin/specdal_pipeline',
          'bin/specdal_info',
          'bin/specdal_gui',
          'bin/specdalqt',
      ],
      entry_points={
          'gui_scripts': ['specdal_gui = specdal.gui.viewer:main'],
      },
      url='https://github.com/EnSpec/SpecDAL/',
      author='Young Lee',
      author_email='ylee546@wisc.edu',
      license='MIT',
      packages=['specdal',  'specdal.gui','specdal.gui.pyqt',
          'specdal.readers','specdal.containers',
          'specdal.operators','specdal.filters'],
      install_requires=['numpy', 'pandas', 'matplotlib', 'scipy','pyqt5'],
      package_data = {'':['specdal/gui/select.png'],
                      'specdal.gui.pyqt':['Assets/*.*']},
      include_package_data = True,
      zip_safe=False,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
          'Programming Language :: Python :: 3',
      ],
      python_requires='>=3'
)
