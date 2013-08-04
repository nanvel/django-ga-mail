import datetime
import contextlib
import os.path

from mock import patch
from gdata.analytics.data import DataFeed
from atom.core import parse

from django.test import TestCase
from django.core import mail 
from django.core.management import call_command


@contextlib.contextmanager
def mock_today(date):
    """
    Context manager for mocking out datetime.date.today() in unit tests.

    Example:
    with mock_today(datetime.date(2011, 2, 3)):
        assert datetime.date.today() == datetime.date(2011, 2, 3)

    """

    class MockDate(datetime.date):
        @classmethod
        def today(cls):
            # Create a copy of date.
            return datetime.date(
                date.year, date.month, date.day
            )
    real_date = datetime.date
    datetime.date = MockDate
    try:
        yield datetime.date
    finally:
        datetime.date = real_date



class GAMailCommandTestCase(TestCase):

    SETTINGS = {
        'GA_PROFILE_ID': 12345678,
        'GA_USERNAME': 'someone@gmail.com',
        'GA_PASSWORD': 'somepass',
        'GA_SOURCE_APP_NAME': 'mysite',
    }

    def test_ga_communicate(self):
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        with self.settings(**self.SETTINGS):
            # freeze time
            with mock_today(datetime.date(2013, 8, 4)):
                with patch('gdata.analytics.client.AnalyticsClient') as client_mock:
                    def get_data_feed(uri):
                        with open(os.path.join(test_data_dir, 'data1.xml'), 'r') as f:
                            return parse(f.read(), DataFeed)
                    client_mock.GetDataFeed.return_value = get_data_feed
                    call_command('ga_mail')
                    self.assertEqual(len(mail.outbox), 1)
                    print mail.outbox[0].body
