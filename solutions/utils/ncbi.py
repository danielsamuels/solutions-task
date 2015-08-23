from django.conf import settings
from django.utils.timezone import now

from ..apps.resources.models import SearchResult

import calendar
import requests
import urllib
import xmltodict


class NCBI(object):

    def estimate(self, term):
        params = {
            'type': 'pdat',
            'retmax': 0,
            'retstart': 0,
            'term': term,
        }

        # Get the number of results for this search.
        url = '{base_url}esearch.fcgi?db=pubmed&retmode=xml&{params}'.format(
            base_url=settings.NCBI_BASE_URL,
            params=urllib.urlencode(params),
        )

        response = requests.get(url)
        parsed_data = xmltodict.parse(response.text)
        return int(parsed_data['eSearchResult']['Count'])

    def search(self, term, **kwargs):
        params = {
            'type': 'pdat',
            'retmax': 0,
            'retstart': 0,
            'term': term,
        }

        # Get the number of results for this search.
        url = '{base_url}esearch.fcgi?db=pubmed&retmode=xml&{params}'.format(
            base_url=settings.NCBI_BASE_URL,
            params=urllib.urlencode(params),
        )

        # Check the min and max year values are valid integers.
        if 'min_year' in kwargs:
            try:
                assert int(kwargs['min_year'])
            except ValueError:
                del kwargs['min_year']

        if 'max_year' in kwargs:
            try:
                assert int(kwargs['max_year'])
            except ValueError:
                del kwargs['max_year']

        # Rather than pulling the actual documents, just use the search to pull
        # the counts. Pulling 3+ million records (for 'cancer') is way too
        # intensive for what this project needs.

        response = requests.get(url)
        parsed_data = xmltodict.parse(response.text)
        total_articles = int(parsed_data['eSearchResult']['Count'])
        year = now().year
        limiter = 0
        count_per_year = {}
        num_seen = 0

        while total_articles > 0:
            obj = None

            if kwargs.get('min_year', False) and int(kwargs['min_year']) > year:
                break

            # Is this year is the current year, how many days in to it are we?
            if year == now().year:
                limiter += now().timetuple().tm_yday
            else:
                # How many days are in this year?
                if calendar.isleap(year):
                    limiter += 366
                else:
                    limiter += 365

                # Is there a SearchResult entry for this term and year?
                try:
                    obj = SearchResult.objects.get(
                        term=term,
                        year=year,
                    )
                except SearchResult.DoesNotExist:
                    pass

            if not obj:
                # Make a call to the API.
                params['reldate'] = limiter
                url = '{base_url}esearch.fcgi?db=pubmed&retmode=xml&{params}'.format(
                    base_url=settings.NCBI_BASE_URL,
                    params=urllib.urlencode(params),
                )

                response = requests.get(url)
                parsed_data = xmltodict.parse(response.text)
                count = int(parsed_data['eSearchResult']['Count'])

                obj = SearchResult(
                    term=term,
                    year=year,
                    num_results=count - num_seen,
                )

                obj.save()

            num_seen += obj.num_results
            total_articles -= obj.num_results

            if kwargs.get('max_year', False) and int(kwargs['max_year']) < year:
                year -= 1
                continue
            else:
                count_per_year[year] = obj.num_results
                year -= 1

        return count_per_year
