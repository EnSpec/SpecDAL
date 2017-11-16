============
Installation
============

SpecDAL is available via pip (``pip install specdal``) or on `Github
<https://github.com/EnSpec/SpecDAL.git/>`_. This page provides
detailed walkthrough of the installation process intended for users
who are not comfortable in Python environment.

Prerequisites
=============

- python3
- pip3

Setting up the virtual environment (recommended)
------------------------------------------------

Although not necessary, it is good practice to install Python packages
in a virtual environment. Virtual environments provide an isolated and
self-contained environment for your Python session, which can help
prevent conflicts across packages. We will walk through the process of
creating one on Ubuntu Linux for demonstration.

- Install virtualenv using pip installer.
  
  ::

     $ pip install --user virtualenv

- Create a directory for storing virtual environments.
  
  ::
     
     $ mkdir ~/venv

- Create a new virtual environment called ``specdal_env`` running python3
  by default. 

  ::
     
     $ virtualenv -p python3 ~/venv/specdal_env

  If you're curious, you can navigate to that directory and find all
  the components that make up a Python environment. For example,
  packages are installed in ``~/venv/specdal_env/lib`` and binaries
  are stored in ``~/venv/specdal_env/bin``.

- Before starting a Python session, we can activate the virtual
  environment as follows.
  
  ::
     
     $ source ~/venv/specdal/bin/activate
      
  Note: On windows, there should be an executable
  ``~/venv/specdal/bin/activate.exe`` with a similar effect.

  You'll notice the name of your virtual environment in
  parentheses. 

  ::
     
     (specdal_env) $ 
     
- Once in this environment, we can install and use ``SpecDAL`` or
  other packages.
  
  ::
     
     (specdal_env) $ ... # install specdal
     (specdal_env) $ ... # write and run programs

- When we're done, we can exit the virtual environment.
  
  ::
     
     $ deactivate

Install via pip
===============

- Stable version
  
::

   $ pip3 install specdal --upgrade

- Latest development version

::

   $ pip3 install specdal --pre

Install from Github
===================

SpecDAL can be found on Enspec's Github `repo
<https://github.com/EnSpec/SpecDAL.git/>`_. Stable release can be
found on ``master`` branch and the development version on ``dev``
branch.

Github walkthrough
------------------

1. Open terminal or Git-bash and navigate to the desired directory,
   ``~/specdal`` for this demo.

   ``cd ~/specdal``

2. The following command will clone the SpecDAL's Github repository.

   ::

      $ git clone https://github.com/EnSpec/SpecDAL.git

   You'll notice a new subdirectory ``SpecDAL`` with the source code.

3. Install SpecDAL.

   ::
      
      $ cd ./SpecDAL
      $ python setup.py install
      
Install in development mode
---------------------------

If you'd like to modify SpecDAL's source, it's useful to install the
package in development mode.

- Install in development mode
  
  ::

     $ python setup.py develop

- Modify the source and run/test it.
  
- Uninstall development mode

  ::

     $ python setup.py develop --uninstall
