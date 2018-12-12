from django.shortcuts import render, HttpResponse, redirect
from contact.models import Contacts
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.http import HttpResponseRedirect
# Create your views here.


def index(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        Contacts.objects.create(user=username, pwd=password)
    user_list = Contacts.objects.all()
    return HttpResponseRedirect("/showPage")
    # return render(request, 'index.html', {'data': user_list})


def showPage(request):
    contact_list = Contacts.objects.all()
    paginator = Paginator(contact_list, 3, 2)

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'showPage.html', {'contacts': contacts})

