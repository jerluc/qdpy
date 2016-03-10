qdpy
====

.. image:: https://api.travis-ci.org/jerluc/qdpy.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/jerluc/qdpy

.. image:: https://readthedocs.org/projects/qdpy/badge/?version=latest
    :alt: Documentation Status
    :target: https://readthedocs.org/projects/qdpy/?badge=latest

`qdpy <http://qdpy.rtfd.org>`_ is a quickly distributed IPython environment

Quick links
-----------

* `Documentation <http://qdpy.rtfd.org>`_
* `Source <https://github.com/jerluc/qdpy>`_

Installation
------------

qdpy requires `IPython <https://ipython.org>`_ to be installed. If you don't already have IPython
installed, your life condition is probably going to dramatically improve after you `download and
install it <https://jupyter.readthedocs.org/en/latest/install.html>`_ :)

.. parsed-literal::

    git clone git@github.com:jerluc/qdpy.git
    cd qdpy
    pip install .

Usage
-----

Once installed, qdpy must be loaded into your IPython shell using the ``%load_ext`` magic:

.. parsed-literal::

    In[1]: %load_ext qdpy

If you'd like to auto-load qdpy anytime you open an IPython shell, add the following to your
IPython config file (usually this is located in `~/.ipython/profile_default/ipython_config.py`):

.. parsed-literal::

    c = get_config()

    # ...

    c.InteractiveShellApp.extensions = [
        'qdpy'
    ]

Once qdpy is loaded, you may join or leave collaboration groups using the ``%join_group <GROUP>`` or
``%leave_group <GROUP>`` magics

The qdpy source code is `hosted on GitHub <https://github.com/jerluc/qdpy>`_.
