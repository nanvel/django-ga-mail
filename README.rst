django-ga-mail app
============

A reusable Django app that sends google analytics statistics by email.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    $ pip install django-ga-mail

To get the latest commit from GitHub

.. code-block:: bash

    $ pip install -e git+git://github.com/nanvel/django-ga-mail.git#egg=django_ga_mail

TODO: Describe further installation steps (edit / remove the examples below):

Add ``django_ga_mail`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'django_ga_mail',
    )


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    $ mkvirtualenv -p python2.7 django-ga-mail
    $ python setup.py install
    $ pip install -r dev_requirements.txt

    $ git co -b feature_branch master
    # Implement your feature and tests
    $ git add . && git commit
    $ git push -u origin feature_branch
    # Send us a pull request for your feature branch
