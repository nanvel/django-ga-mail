import datetime

from gdata.analytics import client as ga_client
from gdata.client import RequestError

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.conf import settings


def ga_communicate(start_date, stop_date, dimensions, metrics, filters=None):
    """
    :param start_date: start date
    :param stop_date: stop date
    :param dimensions: dimensions
    :param metrics: metrics
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
    print feed
    result = {}
    for entry in feed.entry:
        result.update({entry.dimension[0].value: int(entry.metric[0].value)})
    return result


def create_report():
    today = datetime.date.today()
    one_week_ago = today - datetime.timedelta(days=7)
    two_weeks_ago = today - datetime.timedelta(days=14)
    month_ago = today - datetime.timedelta(days=30)
    result = ga_communicate(
                one_week_ago,
                today,
                'ga:visitorType',
                'ga:visits')
    if not result:
        return None
    last_week_count = result.get('New Visitor', 0)
    result = ga_communicate(
                two_weeks_ago,
                one_week_ago,
                'ga:visitorType',
                'ga:visits')
    if not result:
        return None
    previous_week_count = result.get('New Visitor', 0)
    result = ga_communicate(
                month_ago,
                today,
                'ga:visitorType',
                'ga:visits')
    if not result:
        return None
    last_month_count = result.get('New Visitor', 0)
    result = ga_communicate(
                one_week_ago,
                today,
                'ga:pagePath',
                'ga:pageviews')
    if not result:
        return None
    popular_pages = sorted(result.iteritems(), key=lambda a: -a[1])[:20]
    return {
        'site': Site.objects.get_current().domain,
        'week_progress': '%.2f (%d)' % (
                round(100. * (last_week_count - previous_week_count) / last_week_count, 2),
                last_week_count - previous_week_count),
        'month_new_visitors': last_month_count,
        'popular_pages': popular_pages}


def send_report():
    result = create_report()
    if not result:
        return
    from_email = 'ga_mail@%s' % result['site']
    text_content = render_to_string('django_ga_mail/ga_mail.txt', result)
    html_content = render_to_string('django_ga_mail/ga_mail.html', result)
    subject = render_to_string('django_ga_mail/ga_mail_subject.txt', result)
    subject = ' '.join(subject.split('\n'))
    emails = [email[1] for email in settings.MANAGERS]
    msg = EmailMultiAlternatives(subject, text_content, from_email, emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
