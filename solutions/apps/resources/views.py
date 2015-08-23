from django.views.generic import TemplateView

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
