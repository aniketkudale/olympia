import codecs
from datetime import datetime, timedelta
from optparse import make_option
from os import path, unlink

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import commonware.log

from addons.models import File
from stats.models import update_inc, DownloadCount
from zadmin.models import DownloadSource

from . import get_date_from_file, save_stats_to_file


log = commonware.log.getLogger('adi.downloadcountsfromfile')


def is_valid_source(src, fulls, prefixes):
    """Return True if the source is valid.

    A source is valid if it is in the list of valid full sources or prefixed by
    a prefix in the list of valid prefix sources.

    """
    return src in fulls or any(p in src for p in prefixes)


class Command(BaseCommand):
    """Update download count metrics from a file in the database.

    Usage:
    ./manage.py download_counts_from_file <folder> --date=YYYY-MM-DD

    If no date is specified, the default is the day before.
    If not folder is specified, the default is `hive_results/YYYY-MM-DD/`.
    This folder will be located in `<settings.NETAPP_STORAGE>/tmp`.

    We get a row for each "addon download" request, in this format:

        <count> <addon id> <click source>

    There is one DownloadCount entry per addon per day, and each field holds
    the json-ified dict of keys/counters.

    Eg, for the above request:

        date: <the date of the day the queries were made>
        count: <the number of requests for this addon, for this day>
        addon: <the addon that has this id>
        src: {'dp-btn-primary': 1}

    """
    help = __doc__

    option_list = BaseCommand.option_list + (
        make_option('--date', action='store', type='string',
                    dest='date', help='Date in the YYYY-MM-DD format.'),
        make_option('--separator', action='store', type='string', default='\t',
                    dest='separator', help='Field separator in file.'),
    )

    def handle(self, *args, **options):
        start = datetime.now()  # Measure the time it takes to run the script.
        day = options['date']
        if not day:
            day = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        folder = args[0] if args else 'hive_results'
        folder = path.join(settings.TMP_PATH, folder, day)
        sep = options['separator']
        filepath = path.join(folder, 'download_counts.hive')
        # Make sure we're not trying to update with mismatched data.
        if get_date_from_file(filepath, sep) != day:
            raise CommandError('%s file contains data for another day' %
                               filepath)
        # First, make sure we don't have any existing counts for the same day,
        # or it would just increment again the same data.
        DownloadCount.objects.filter(date=day).delete()

        # Memoize the files to addon relations and the DownloadCounts.
        download_counts = {}
        # Perf: preload all the files once and for all.
        # This builds a dict where each key (the file_id we get from the hive
        # query) has the addon_id as value.
        files_to_addon = dict(File.objects.values_list('id',
                                                       'version__addon_id'))

        # Only accept valid sources, which are listed in the DownloadSource
        # model. The source must either be exactly one of the "full" valid
        # sources, or prefixed by one of the "prefix" valid sources.
        fulls = set(DownloadSource.objects.filter(type='full').values_list(
            'name', flat=True))
        prefixes = DownloadSource.objects.filter(type='prefix').values_list(
            'name', flat=True)

        with codecs.open(filepath, encoding='utf8') as count_file:
            for index, line in enumerate(count_file):
                if index and (index % 1000000) == 0:
                    log.info('Processed %s lines' % index)

                splitted = line[:-1].split(sep)

                if len(splitted) != 4:
                    log.debug('Badly formatted row: %s' % line)
                    continue

                day, counter, file_id, src = splitted
                try:
                    file_id, counter = int(file_id), int(counter)
                except ValueError:  # Badly formatted? Drop.
                    continue

                if not is_valid_source(src, fulls=fulls, prefixes=prefixes):
                    continue

                # Does this file exist?
                if file_id in files_to_addon:
                    addon_id = files_to_addon[file_id]
                else:
                    continue

                # Memoize the DownloadCount.
                if addon_id in download_counts:
                    dc = download_counts[addon_id]
                else:
                    dc = DownloadCount(date=day, addon_id=addon_id, count=0)
                    download_counts[addon_id] = dc

                # We can now fill the DownloadCount object.
                dc.count += counter
                dc.sources = update_inc(dc.sources, src, counter)

        # Create in bulk: this is much faster.
        DownloadCount.objects.bulk_create(download_counts.values(), 100)
        for download_count in download_counts.values():
            save_stats_to_file(download_count)
        log.info('Processed a total of %s lines' % (index + 1))
        log.debug('Total processing time: %s' % (datetime.now() - start))

        # Clean up file.
        log.debug('Deleting {path}'.format(path=filepath))
        unlink(filepath)
