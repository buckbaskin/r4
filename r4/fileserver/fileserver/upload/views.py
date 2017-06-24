from django.shortcuts import render, redirect
from django.http import HttpResponse
from upload.forms import DocumentForm
from upload.models import Document

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You are at the uploads index.")

def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'model_form_upload.html', {
        'form':form
    })

def home(request):
    documents = Document.objects.all()
    return render(request, 'home.html',{'documents':documents})
