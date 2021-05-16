from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.files import File #I added
#from . import form
from .forms import NameForm
from .forms import ContactForm
from django.core.mail import send_mail #for contactForm class
from django.core.mail import EmailMessage #for sending email with attachment
from django.core.files.storage import FileSystemStorage #for storing uploaded files in media

#from .test import *
from .prediction import *

#import subprocess
from subprocess import run, PIPE #For calling external python script
import sys



# Create your views here.

def get_sequence(request):
    #return HttpResponse("Hello Python!!")
    # if this is a POST request we need to process the form data
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            
            # process the data in form.cleaned_data as required
            # ...
            #1st parameter - input file

            # Uploaded file saving

            #Deleting the all the media files before uploading:
            dir = './media/'
            for file in os.scandir(dir):
                os.remove(file.path)

            uploaded_file=request.FILES['pdb_file']
            print(uploaded_file.name)
            fs = FileSystemStorage()
            pdb_file_name = fs.save(uploaded_file.name, uploaded_file)
            pdb_file_path = fs.url(pdb_file_name)
            pdb_file_path = '.'+pdb_file_path
            print(pdb_file_path)

            # 2nd parameter
            chain_name = form.cleaned_data['chain_name']
            # 3rd parameter
            prediction_begin_range = str(form.cleaned_data['prediction_begin_range'])
            prediction_end_range = str(form.cleaned_data['prediction_end_range'])
            pred_range=prediction_begin_range + ',' + prediction_end_range 
            # 4th parameter
            model_name = form.cleaned_data['model_name']
            # 5th parameter
            recipient = form.cleaned_data['recipient'] #for email
            
            #output processing
            original_seq, predicted_seq, output_prob, image_names = main(pdb_file_path, chain_name, pred_range, model_name, pdb_file_name)
            
            ###########Email sending with attachment part STARTS here##############
            
            subject = "[no reply] ProDCoNN server: job finished"
            message="Please have the attached two files as your protein prediction results."
            sender = "arunima1590@gmail.com"
            #recipients = ['info@example.com']
            #if cc_myself:
            #    recipients.append(sender)
            '''
            #This works but not for sending attachments.
            send_mail(subject, message, sender, [recipient])
            '''
            #email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [recipient]) 
            #The above didn't work, but need to be worked!!!
            email = EmailMessage(subject, message, sender, [recipient])

            #seq_file_name = pdb_file_name + '_seq.txt'
            prob_file_name = pdb_file_name + '_prob.txt'
            result_file_path = './pred_result/static/pred_result/result/'

            #email.attach_file(result_file_path+seq_file_name)
            email.attach_file(result_file_path+prob_file_name)
            #email.send() #will activate it later

            #############Email sending with attachment part ends here #################


            global pass_val_prob
            def pass_val_prob():
                return output_prob

            '''
            #Another way of downloading the file, another download function option
            fl_path = result_file_path
            filename = "result_"+pdb_file_name+".txt"
            fl = open(fl_path, 'r’)
            mime_type, _ = mimetypes.guess_type(fl_path)
            response = HttpResponse(fl, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
            '''
            return render(request, 'pred_result/pred_result.html', {'original_seq': original_seq, 'predicted_seq': predicted_seq, 'image_names': image_names, 'model_name': model_name, })

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'get_sequence/get_sequence.html', {'form': form,})



def download_pred_prob(request):
    output = pass_val_prob() #Calling pass_val_prob() function which was declared & defined in get_squence view
    filename = "prediction_probability.txt"
    file_data = output
    response = HttpResponse(file_data, content_type='/application/text')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    return response



    
#Example ContactForm for future reference
def send_email(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        if form.is_valid():
            #subject = form.cleaned_data['subject']
            subject = "[no reply] ProDCoNN server: job finished"
            #message = form.cleaned_data['message']
            message="Please have the attached files as the result"
            #sender = form.cleaned_data['sender']
            sender = "arunima1590@gmail.com"
            #cc_myself = form.cleaned_data['cc_myself']
            recipient = form.cleaned_data['subject']
            #recipients = ['info@example.com']

            #if cc_myself:
            #    recipients.append(sender)

            send_mail(subject, message, sender, recipient)
            return HttpResponseRedirect('get_sequence/pred_result.html')
    else:
            form = ContactForm()
    #return render(request, 'get_sequence/.html', {'form': form})
    return render(request, 'get_sequence/pred_result.html', {'form': form,})
