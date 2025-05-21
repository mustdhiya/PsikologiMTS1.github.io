from django.shortcuts import render

def index(request):
    return render(request, 'app/index.html')

def scoring(request):
    return render(request, 'app/scoring.html')

def certif1(request):
    return render(request, 'app/Certif1.html')

def certif2(request):
    return render(request, 'app/Certif2.html')

def certif3(request):
    return render(request, 'app/Certif3.html')

def certif4(request):
    return render(request, 'app/Certif4.html')
