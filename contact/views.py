from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.


def contact(request):
    #return HttpResponse("Hello Python!!")
    return render(request, 'contact/contact.html')