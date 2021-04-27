from django.shortcuts import render

# Create your views here.
def intro(request):
    details={
    'title': "Protein Sequence Prediction",
    'intro': " It's a website for Protein Sequence Prediction "
    }

    return render(request, 'home/home.html', details)
