from django.views.generic import View
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate


class HomeView(TemplateView):

    template_name = 'demo/home.html'


class ProfileView(TemplateView):

    template_name = 'demo/profile.html'
    permissions = ['user__is_authenticated->log_in']


class AccessDeniedView(TemplateView):

    template_name = 'demo/access_denied.html'
    permissions = ['user__is_authenticated']


class LogInView(TemplateView):

    template_name = 'demo/log_in.html'

    def post(self, request, *args, **kwargs):
        user = authenticate(username='admin', password='admin')
        login(request, user)
        return HttpResponseRedirect(reverse('profile'))


class LogOutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('home'))


home_view = HomeView.as_view()
profile_view = ProfileView.as_view()
access_denied_view = AccessDeniedView.as_view()
log_in_view = LogInView.as_view()
log_out_view = LogOutView.as_view()