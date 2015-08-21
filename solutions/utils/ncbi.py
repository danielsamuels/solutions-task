from django.conf import settings

from ..apps.resources.models import Resource

import datetime
import requests
import urllib
import xmltodict


class NCBI(object):

    def _request(self, module, method, **kwargs):
        data = {}

        if 'data' in kwargs:
            data = kwargs.pop('data')

        url = '{base_url}{module}.fcgi?db=pubmed&retmode=xml&{params}'.format(
            base_url=settings.NCBI_BASE_URL,
            module=module,
            params=urllib.urlencode(kwargs),
        )

        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, data=data)

        if response.status_code == requests.codes.OK:
            return xmltodict.parse(response.text)
        else:
            print response.status_code, response.text

    def search(self, term):
        params = {
            'reldate': 365,
            'type': 'pdat',
            'retmax': 100000,
        }

        results = self._request('esearch', 'GET', term=term, **params)

        # From the list of IDs we've had returned, remove any which are already
        # in our database (to make the ensuing request faster).
        # The values stored in `pmids` are unicode strings and the values in
        # `stored_pmids` are integers, so we cannot do a direct set subtraction
        # without first recasting the values.

        pmids = set(results['eSearchResult']['IdList']['Id'])
        stored_pmids = Resource.objects.values_list('pmid', flat=True)

        stored_pmids = set(unicode(pmid) for pmid in stored_pmids)

        unstored_pmids = pmids - stored_pmids

        if unstored_pmids:
            articles = self._request('efetch', 'POST', data={
                'id': unstored_pmids
            })

            article_set = articles['PubmedArticleSet']

            if 'PubmedArticle' in article_set:
                for article in article_set['PubmedArticle']:
                    pmid = article['MedlineCitation']['PMID']['#text']

                    resource, created = Resource.objects.get_or_create(pmid=pmid)

                    date_created = article['MedlineCitation']['DateCreated']
                    resource.date_created = datetime.date(
                        int(date_created['Year']),
                        int(date_created['Month']),
                        int(date_created['Day'])
                    )

                    # Not every Article has been revised, so check for the value before
                    # attempting to parse the data.

                    if 'DateRevised' in article['MedlineCitation']:
                        date_revised = article['MedlineCitation']['DateRevised']
                        resource.date_revised = datetime.date(
                            int(date_revised['Year']),
                            int(date_revised['Month']),
                            int(date_revised['Day'])
                        )

                    resource.save()

            if 'PubmedBookArticle' in article_set:
                for book in article_set['PubmedBookArticle']:
                    pmid = book['BookDocument']['PMID']['#text']

                    resource, created = Resource.objects.get_or_create(pmid=pmid)

                    date_created = book['PubmedBookData']['History']['PubMedPubDate'][0]
                    resource.date_created = datetime.date(
                        int(date_created['Year']),
                        int(date_created['Month']),
                        int(date_created['Day'])
                    )

                    resource.save()

        return Resource.objects.filter(
            pmid__in=pmids,
        )
