import sys

from django.conf import settings


def main():
    settings.configure(
        INSTALLED_APPS=(
            'django.contrib.sites',
            'django_ga_mail',
        ),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        SITE_ID=1,
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )

    from django.test.simple import DjangoTestSuiteRunner

    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(['django_ga_mail',])
    if failures:
        sys.exit(failures)


if __name__ == '__main__':
    main()
