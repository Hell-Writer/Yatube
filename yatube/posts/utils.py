from django.core.paginator import Paginator


def pagination(request, model, page_num):
    paginator = Paginator(model, page_num)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
