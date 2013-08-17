django-ga-mail app
==================

A reusable Django app that sends google analytics report by email.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    $ pip install django-ga-mail

To get the latest commit from GitHub

.. code-block:: bash

    $ pip install -e git+git://github.com/nanvel/django-ga-mail.git#egg=django_ga_mail

Add ``django_ga_mail`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'ga_mail',
    )

Specify next variables in settings:

.. code-block:: python

    GA_PROFILE_ID = 12345678
    GA_USERNAME = 'some.user@gmail.com'
    # don't use your working account here,
    # create another one for analytics and give it access to ga profile
    GA_PASSWORD = 'somepass'
    GA_SOURCE_APP_NAME = 'some.site',
    ANALYTICS_BLOCKS = (
        'unique_visits_7days_today',
        'visits_7days_today_vs_14days_7days',
        'pageviews_7days_today')

Check that MANAGERS variable contains necessary emails.

Available blocks:

    - visits_7days_today
    - unique_visits_7days_today
    - visits_7days_today_vs_14days_7days
    - unique_visits_7days_today_vs_14days_7days
    - pageviews_7days_today

Call ``python manage.py ga_mail`` to send analytics report.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    $ virtualenv .env --no-site-packages
    $ source .env/bin/activate
    $ python setup.py install
    $ pip install -r test_requirements.txt

    $ git co -b feature_branch master
    # Implement your feature and tests
    $ git add . && git commit
    $ git push -u origin feature_branch
    # Send us a pull request for your feature branch
