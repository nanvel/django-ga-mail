from mock import patch

from django.test import TestCase
from django.core import mail 
from django.core.management import call_command


class GAMailCommandTestCase(TestCase):

    SETTINGS = {
        'GA_PROFILE_ID': 123456,
        'GA_USERNAME': 'some.manager@gmail.com',
        'GA_PASSWORD': 'somepass',
        'GA_SOURCE_APP_NAME': 'some.site',
        'ANALYTICS_BLOCKS': (
            'new_visitors_7days_today',
            'new_visitors_7days_today_vs_14days_7days',
            'pageviews_7days_today'),
        'MANAGERS': (
            ('Some Admin', 'some.admin@gmail.com'),
        )
    }

    def test_ga_communicate(self):
        with self.settings(**self.SETTINGS):
            def ga_communicate(self, start_date, stop_date, metrics, dimensions, filters=None):
                return {'Visitor': 2, 'New Visitor': 1}
            with patch('ga_mail.utils.AnalyticsSource.ga_communicate', ga_communicate):
                call_command('ga_mail')
                self.assertEqual(len(mail.outbox), 1)
                content = mail.outbox[0].body
                self.assertIn('100.0', content)
                self.assertIn('New Visitor', content)
