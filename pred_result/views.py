from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def pred_result(request):
    #return HttpResponse("Hello Python!!")
    return render(request, 'pred_result/pred_result.html')
