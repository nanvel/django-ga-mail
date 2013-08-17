from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ...utils import send_report


class Command(BaseCommand):
    args = '<No args>'
    help = 'Send analytics report by mail'

    def handle(self, *args, **options):
        send_report(blocks=settings.ANALYTICS_BLOCKS)