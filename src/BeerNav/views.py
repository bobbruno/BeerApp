from django.http.response import HttpResponseRedirect
from django.views.generic import DetailView, TemplateView, FormView
from django_tables2 import SingleTableView

from BeerNav.forms import PollForm
from BeerNav.models import Beer
import BeerNav.skModels as skModels
from BeerNav.tables import BeerTable


#  I have to change this view to get a nice result and then allow the user to go to beer details
#  (maybe as a subform at the bottom)


class BeerListView(SingleTableView):
    model = Beer
    table_class = BeerTable

    def get_queryset(self):
        #  return SingleTableView.get_queryset(self)(self, request):
        BeerList = skModels.get_nearest(self.request.session['pollData'], 50)
        return Beer.objects.filter(pk__in=BeerList)


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
