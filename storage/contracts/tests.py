from django.test import TestCase

# Create your tests here.
string = '/contracts/&page=1'
def cut_page(string):
    if '?page' in string:
        return string.rsplit('?page', 1)[0]
    if '&page' in string:
        return string.rsplit('&page', 1)[0]

print(cut_page(string))