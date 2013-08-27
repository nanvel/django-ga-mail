import datetime

from gdata.analytics import client as ga_client
from gdata.client import RequestError

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.conf import settings


class AnalyticsSource(object):
    """
    Functions names pattern:
    {metrics}_{dimensions}_{filters}_{-start_date}_{-enddate}
    """

    def __init__(self):
        self.today = datetime.date.today()

    def ga_communicate(self, start_date, stop_date, metrics, dimensions, filters=None):
        """
        :param start_date: start date
        :param stop_date: stop date
        :param metrics: metrics
        :param dimensions: dimensions
        :params filters: dimension/value couples, example: 'ga:pagePath=~/,ga:pagePath=~/home/'

        dimensions and metrics:
        https://developers.google.com/analytics/devguides/reporting/core/dimsmets#cats=visitor
        """

        PROFILE_ID = 'ga:%d' % settings.GA_PROFILE_ID
        client = ga_client.AnalyticsClient(source=settings.GA_SOURCE_APP_NAME)
        client.client_login(
                settings.GA_USERNAME,
                settings.GA_PASSWORD,
                settings.GA_SOURCE_APP_NAME,
                service='analytics')
        query_uri = ga_client.DataFeedQuery({
                'ids': PROFILE_ID,
                'start-date': start_date,
                'end-date': stop_date,
                'dimensions': dimensions,
                'metrics': metrics,
            })
        if filters:
            query_uri.query['filters'] = filters
        try:
            feed = client.GetDataFeed(query_uri)
        except RequestError as e:
            return None
        result = {}
        for entry in feed.entry:
            result.update({entry.dimension[0].value: int(entry.metric[0].value)})
        return result

    def visits_visitortype_7days_today(self):
        result = getattr(self, '_visits_visitortype_7days_today', None)
        if result:
            return result
        one_week_ago = self.today - datetime.timedelta(days=7)
        result = self.ga_communicate(
                start_date=one_week_ago,
                stop_date=self.today,
                metrics='ga:visits',
                dimensions='ga:visitorType')
        self._visits_visitortype_7days_today = result
        return result

    def visits_visitortype_14days_7days(self):
        result = getattr(self, '_visits_visitortype_14days_7days', None)
        if result:
            return result
        one_week_ago = self.today - datetime.timedelta(days=7)
        two_weeks_ago = self.today - datetime.timedelta(days=14)
        result = self.ga_communicate(
                start_date=two_weeks_ago,
                stop_date=one_week_ago,
                metrics='ga:visits',
                dimensions='ga:visitorType')
        self._visits_visitortype_14days_7days = result
        return result

    def visits_visitortype_30days_today(self):
        result = getattr(self, '_visits_visitortype_30days_today', None)
        if result:
            return result
        month_ago = self.today - datetime.timedelta(days=30)
        result = self.ga_communicate(
                start_date=month_ago,
                stop_date=self.today,
                metrics='ga:visits',
                dimensions='ga:visitorType')
        self._visits_visitortype_30days_today = result
        return result

    def pageviews_pagepath_7days_today(self):
        result = getattr(self, '_pageviews_pagepath_7days_today', None)
        if result:
            return result
        one_week_ago = self.today - datetime.timedelta(days=7)
        result = self.ga_communicate(
                start_date=one_week_ago,
                stop_date=self.today,
                metrics='ga:pageviews',
                dimensions='ga:pagePath')
        self._pageviews_pagepath_7days_today = result
        return result

    def countries_30days_today(self):
        result = getattr(self, '_countries', None)
        if result:
            return result
        month_ago = self.today - datetime.timedelta(days=30)
        result = self.ga_communicate(
                start_date=month_ago,
                stop_date=self.today,
                metrics='ga:visits',
                dimensions='ga:country')
        self._countries_30days_today = result
        return result


class Report(object):

    TEMPLATE_HEADER = 'ga_mail/header.{ext}'
    TEMPLATE_BLOCK = 'ga_mail/block_{type}.{ext}'
    TEMPLATE_FOOTER = 'ga_mail/footer.{ext}'

    def __init__(self, name=None):
        self.site = Site.objects.get_current().domain
        if not name:
            name = 'Analytics for %s' % self.site
        self.name = name
        self.text = render_to_string(
                self.TEMPLATE_HEADER.format(ext='txt'),
                {'name': name})
        self.html = render_to_string(
                self.TEMPLATE_HEADER.format(ext='html'),
                {'name': name})

    def add_block(self, type, context):
        self.text += render_to_string(
                self.TEMPLATE_BLOCK.format(type=type, ext='txt'),
                context)
        self.html += render_to_string(
                self.TEMPLATE_BLOCK.format(type=type, ext='html'),
                context)

    def send(self):
        self.text += render_to_string(
                self.TEMPLATE_FOOTER.format(ext='txt'),
                {'name': self.name})
        self.html += render_to_string(
                self.TEMPLATE_FOOTER.format(ext='html'),
                {'name': self.name})
        from_email = 'ga_mail@%s' % self.site
        emails = [email[1] for email in settings.MANAGERS]
        msg = EmailMultiAlternatives(self.name, self.text, from_email, emails)
        msg.attach_alternative(self.html, "text/html")
        msg.send()


def send_report(blocks):
    report = Report()
    source = AnalyticsSource()
    for block in blocks:
        # visitors
        if block == 'returning_visitors_7days_today':
            result = source.visits_visitortype_7days_today()
            if not result:
                continue
            count = result.get('Returning Visitor', 0)
            report.add_block(
                    type='value',
                    context={
                        'title': 'Returning visitors for last week',
                        'value': count})
        elif block == 'new_visitors_7days_today':
            result = source.visits_visitortype_7days_today()
            if not result:
                continue
            count = result.get('New Visitor', 0)
            report.add_block(
                    type='value',
                    context={
                        'title': 'New visitors for last week',
                        'value': count})
        elif block == 'new_visitors_30days_today':
            result = source.visits_visitortype_30days_today()
            if not result:
                continue
            count = result.get('New Visitor', 0)
            report.add_block(
                    type='value',
                    context={
                        'title': 'New visitors for last month',
                        'value': count})
        # increase
        elif block == 'new_visitors_7days_today_vs_14days_7days':
            result1 = source.visits_visitortype_7days_today()
            if not result1:
                continue
            count1 = result1.get('New Visitor', 0)
            result2 = source.visits_visitortype_14days_7days()
            if not result2:
                continue
            count2 = result2.get('New Visitor', 0)
            if count2 == 0:
                continue
            report.add_block(
                    type='value',
                    context={
                        'title': 'New visitors for last week vs new visitors week ago',
                        'value': '%.2f%%' % round(100. * count1 / count2, 2)})
        # proportions
        elif block == 'new_visitors_7days_today_vs_returning_visitors_7days_today':
            result1 = source.visits_visitortype_7days_today()
            if not result1:
                continue
            count1 = result1.get('New Visitor', 0)
            result2 = source.visits_visitortype_7days_today()
            if not result2:
                continue
            count2 = result2.get('Returning Visitor', 0)
            if count2 == 0:
                continue
            report.add_block(
                    type='value',
                    context={
                        'title': 'New visitors for last week vs returning visitors',
                        'value': '%.2f%%' % round(100. * count1 / count2, 2)})
        # pageviews
        elif block == 'pageviews_7days_today':
            result = source.pageviews_pagepath_7days_today()
            if not result:
                continue
            popular_pages = sorted(result.iteritems(), key=lambda a: -a[1])[:10]
            report.add_block(
                    type='list',
                    context={
                        'title': 'Most popular pages',
                        'list': popular_pages})
        # auditory
        elif block == 'countries_30days_today':
            result = source.countries_30days_today()
            if not result:
                continue
            countries = sorted(result.iteritems(), key=lambda a: -a[1])[:10]
            report.add_block(
                    type='list',
                    context={
                        'title': 'Countries list',
                        'list': countries})
    report.send()
