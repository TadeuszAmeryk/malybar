# -*- coding: utf-8 -*-

# from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . import models
from . import forms
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.forms.models import modelformset_factory
from django.template.response import TemplateResponse


def index(request):
    """Strona główna"""
    kontekst = {'komunikat': 'Witaj w aplikacji Pizza!'}
#    return render(request, 'pizza/index.html', kontekst)
    return TemplateResponse(request, 'pizza/index.html', kontekst)


@method_decorator(login_required, 'dispatch')
class PizzaCreate(CreateView):
    """Widok dodawania pizzy i skladników."""

    model = models.Pizza
    form_class = forms.PizzaForm
    success_url = reverse_lazy('pizza:lista')  # '/pizza/lista'

    def get_context_data(self, **kwargs):
        context = super(PizzaCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            context['skladniki'] = forms.SkladnikiFormSet(self.request.POST)
        else:
            context['skladniki'] = forms.SkladnikiFormSet()
        return context

    def form_valid(self, form):
        form.instance.autor = self.request.user
        context = self.get_context_data()
        skladniki = context['skladniki']
        if form.is_valid() and skladniki.is_valid():
            self.object = form.save()
            skladniki.instance = self.object
            skladniki.save()
            return super(PizzaCreate, self).form_valid(form)
        return self.form_invalid(form, skladniki)

    def form_invalid(self, form, skladniki):
        errors = skladniki.non_form_errors()
        if skladniki.total_form_count() == 0:
            skladniki = forms.SkladnikiFormSet()
            skladniki._non_form_errors = errors
        return self.render_to_response(
            self.get_context_data(form=form, skladniki=skladniki)
        )


@method_decorator(login_required, 'dispatch')
class PizzaUpdate(UpdateView):
    """Widok aktualizuacji"""

    model = models.Pizza
    form_class = forms.PizzaForm
    success_url = reverse_lazy('pizza:lista')  # '/pizza/lista'

    def get_context_data(self, **kwargs):
        context = super(PizzaUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            context['skladniki'] = forms.SkladnikiFormSet(
                self.request.POST,
                instance=self.object)
        else:
            context['skladniki'] = forms.SkladnikiFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        form.instance.autor = self.request.user
        context = self.get_context_data()
        skladniki = context['skladniki']
        if form.is_valid() and skladniki.is_valid():
            self.object = form.save()
            skladniki.save()
            return HttpResponseRedirect(self.get_success_url())
        return self.form_invalid(form, skladniki)

    def form_invalid(self, form, skladniki):
        errors = skladniki.non_form_errors()
        if skladniki.total_form_count() == 0:
            skladniki = forms.SkladnikiFormSet()
            skladniki._non_form_errors = errors
        return self.render_to_response(
            self.get_context_data(form=form, skladniki=skladniki)
        )


@method_decorator(login_required, 'dispatch')
class PizzaDelete(DeleteView):
    model = models.Pizza
    template_name = 'pizza/pizza_usun.html'
    success_url = reverse_lazy('pizza:list')  # '/pizza/lista'

    def get_context_data(self, **kwargs):
        context = super(PizzaDelete, self).get_context_data(**kwargs)
        pizza = models.Pizza.objects.get(pk=self.object.id)
        SkladnikFormSet = modelformset_factory(
            models.Skladnik,
            fields=('nazwa',))
        context['skladniki'] = SkladnikFormSet(
            queryset=models.Skladnik.objects.filter(nazwa=pizza))
        return context
