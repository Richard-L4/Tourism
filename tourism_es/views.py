from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, ContactForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CardText
from django.core.paginator import Paginator


def index(request):
    return render(request, 'index.html', {'active_tab': 'index'})


def about(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been submitted")
            return redirect('about')
    else:
        form = ContactForm()
    return render(request, 'about.html', {'active_tab': 'about', 'form': form})


def events(request):
    # cards for card: cards in return render and for paginator later
    card_texts = CardText.objects.all().order_by('id')
    paginator = Paginator(card_texts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'events.html', {
        'active_tab': 'events', 'page_obj': page_obj})


def event_details(request, pk):
    # safer way to get the event; avoids crashing if ID doesn't exist
    event = get_object_or_404(CardText, id=pk)

    return render(request, 'event-details.html', {
        'active_tab': 'event-details',
        'event': event,  # pass the event to the template
    })


def edit_comment(request):
    return render(request, 'edit-comment.html', {'active_tab': 'edit-comment'})


def delete_comments(request):
    return render(request, 'delete-comments.html',
                  {'active_tab': 'delete-comments'})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are logged in as {username}")
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html',
                  {'active_tab': 'login', 'form': form})


def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return render(request, 'logout.html', {'active_tab': 'logout'})


def confirm_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return render(request, 'confirm-logout.html',
                  {'active_tab': 'confirm-logout'})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f"Account created for {username}! You can log in."
            )
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html',
                  {'active_tab': 'register', 'form': form})
