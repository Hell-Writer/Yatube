from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import CreateView

from .forms import ContactForm, CreationForm
from .models import Contact


class SignUpView(CreateView):
    form_class = CreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('posts:index')


class ContactView(CreateView):
    form_class = ContactForm
    template_name = 'users/contact.html'
    contact = Contact()
    form = ContactForm(instance=contact)
    context = {'form': form}
    success_url = reverse_lazy('posts:index')


class LoginView(CreateView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('posts:index')


class LogoutView(CreateView):
    template_name = 'users/logout.html'


def password_change(request):
    template = 'users/password_change_form.html'
    return render(request, template)


def password_change_done(request):
    template = 'users/password_change_done.html'
    return render(request, template)


def password_reset(request):
    template = 'users/password_reset_form.html'
    return render(request, template)


def password_reset_done(request):
    template = 'users/password_reset_done.html'
    send_mail('Сброс пароля',
              'Чтобы сбросить пароль, перейдите по ссылке: ',
              'from@example.com',
              ['to@example.com'],
              fail_silently=False,)
    return render(request, template)


def password_reset_confirm(request):
    template = 'users/password_reset_confirm.html'
    return render(request, template)


def password_reset_complete(request):
    template = 'users/password_reset_complete.html'
    return render(request, template)
