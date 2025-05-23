from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html')

def scoring(request):
    return render(request, 'main/scoring.html')

def certif1(request):
    return render(request, 'main/Certif1.html')

def certif2(request):
    return render(request, 'main/Certif2.html')

def certif3(request):
    return render(request, 'main/Certif3.html')

def certif4(request):
    return render(request, 'main/Certif4.html')
