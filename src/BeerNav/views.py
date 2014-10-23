from django.http.response import HttpResponseRedirect
from django.views.generic import ListView, DetailView, TemplateView, FormView

from BeerNav.forms import PollForm
from BeerNav.models import Beer
import BeerNav.skModels as skModels


#  I have to change this view to get a nice result and then allow the user to go to beer details
#  (maybe as a subform at the bottom)
class BeerListView(ListView):
    model = Beer
    template_name = "BeerNav/beer_list.html"

    def get_queryset(self):
        #  return SingleTableView.get_queryset(self)(self, request):
        self.ranks, BeerList = skModels.get_nearest(self.request.session['pollData'], 50)
        return Beer.objects.filter(pk__in=BeerList).values('pk', 'name', 'brewery', 'style__name',
                                                           'IBU', 'ABV', 'country', 'overallRating', 'styleRating')

    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        for row in context['object_list']:
            row['rank'] = self.ranks[row['pk']]
        return context


class BeerView(DetailView):
    model = Beer


class HomePageView(TemplateView):
    template_name = "index.html"


class PollView(FormView):
    template_name = 'BeerNav/poll.html'
    form_class = PollForm
    success_url = '/beers'

    def form_valid(self, form):
        #  Save the data for the user here - probably will have to change the form to a bound form
        self.request.session['pollData'] = form.cleaned_data
        return HttpResponseRedirect(self.get_success_url())
