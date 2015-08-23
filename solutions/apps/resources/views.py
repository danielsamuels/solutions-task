from django.db.models import Sum
from django.http import JsonResponse
from django.views.generic import TemplateView, View

from .models import SearchResult
from ...utils.ncbi import NCBI


class HomepageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        ncbi = NCBI()

        if self.request.GET.get('term', False):
            # Get the number of articles in this search and estimate the time it
            # will take to pull the data down.
            items = int(ncbi.estimate(self.request.GET['term']))

            # Get the number of items already in the database.
            db_items = SearchResult.objects.filter(
                term=self.request.GET['term']
            ).aggregate(Sum('num_results'))['num_results__sum']

            if not db_items:
                db_items = 0

            items -= db_items

            context['estimate'] = items / 1050.0

        return context


class AJAXDataView(View):
    http_method_types = ['get']

    def get(self, request, *args, **kwargs):
        ncbi = NCBI()

        if self.request.GET.get('term', False):
            data = ncbi.search(
                self.request.GET['term'],
                min_year=self.request.GET.get('min_year', False),
                max_year=self.request.GET.get('max_year', False),
            )
        else:
            data = {}

        # Check the min and max year values are valid integers.
        request_data = self.request.GET.dict()

        if 'min_year' in request_data:
            try:
                assert int(request_data['min_year'])
            except ValueError:
                del request_data['min_year']

        if 'max_year' in request_data:
            try:
                assert int(request_data['max_year'])
            except ValueError:
                del request_data['max_year']

        if request_data.get('min_year'):
            data = {
                key: value
                for key, value in data.iteritems()
                if key >= int(request_data['min_year'])
            }

        if request_data.get('max_year'):
            data = {
                key: value
                for key, value in data.iteritems()
                if key <= int(request_data['max_year'])
            }

        return JsonResponse(data)
