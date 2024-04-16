from products.utils import menu

from contracts.models import Action


def get_menu(request):
    return {'menu': menu}

def get_last_updates(request):
    last_updates = Action.objects.all().order_by("-pk")[:10]
    return {'last_updates': last_updates}
