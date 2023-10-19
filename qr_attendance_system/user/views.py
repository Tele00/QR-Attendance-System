from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Create your views here.
def loginpage(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            return render(request, "user/login.html", {
                "error": "Invalid username or password"
            })
    
    return render(request, "user/login.html")

    form = UserCreationForm()
    return render(request, 'user/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('confirm-password')

        if username != '' and email != '' and pass1 != '' and pass2 != '':
            if pass1 == pass2:
                user = User.objects.create_user(username,email, pass1)
                user.save()
            else:
                return render(request, 'user/login.html', {
                    "message": "Passwords don't match."
                })
        else:
            return render(request, 'user/login.html', {
                "message": "All fields are required"
            })
        return render(request, 'user/login.html', {
            "messagesuccess": "Account created Successfully! Log In."
        })


    return HttpResponseRedirect(reverse("login"))

def logoutpage(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url='login')
def index(request):
    return render(request, "user/index.html")