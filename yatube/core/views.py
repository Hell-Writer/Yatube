from django.shortcuts import render
from django.views.decorators.cache import cache_page


def page_not_found(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


@cache_page(600)
def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')


def page_forbidden(request, exception):
    render(request, 'core/403.html', status=403)


def page_server_error(request, exception):
    render(request, 'core/500.html', status=500)
