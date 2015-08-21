from django.views.generic import TemplateView

from ...utils.ncbi import NCBI


class HomepageView(TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)

        ncbi = NCBI()
        print ncbi.search('asthma')

        return context
