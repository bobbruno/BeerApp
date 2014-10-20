from django.http.response import HttpResponseRedirect
from django.views.generic import DetailView, ListView, TemplateView, FormView

from BeerNav.forms import PollForm
from BeerNav.models import Beer


#  I have to change this view to get a nice result and then allow the user to go to beer details
#  (maybe as a subform at the bottom)
class BeerListView(ListView):
    model = Beer
    paginate_by = 10

    def get(self, request):
        print request.session['pollData']
        #  This is where I have to actually find the beers to recommend
        #  BeerList = get_nearest(request.session['pollData'])
        BeerList = [189385, 195778, 204101, 208450, 163204, 113855, 208445, 239419, 213248, 89836]
        self.queryset = Beer.objects.filter(pk__in=BeerList)
        return super(BeerListView, self).get(request)


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
