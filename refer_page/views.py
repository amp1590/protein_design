from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.


def refer_page(request):
    #return HttpResponse("Hello Python!!")
    return render(request, 'refer_page/refer_page.html')