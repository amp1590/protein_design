from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def pred_result(request):
    #return HttpResponse("Hello Python!!")
    return render(request, 'pred_result/pred_result.html')

#No need to add this since I'm including this in get_sequence
def download(request):
    if request.method == 'POST':
        #output=pass_val()
        filename = "pred_result.txt"
        file_data = "I am Arunima"
        response = HttpResponse(file_data, content_type='/application/text')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
        return response