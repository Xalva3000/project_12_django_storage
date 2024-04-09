from django.http import HttpResponseNotFound, HttpRequest


def page_not_found(request: HttpRequest, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")