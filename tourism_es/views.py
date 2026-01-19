from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def events(request):
    return render(request, 'events.html')


def event_details(request):
    return render(request, 'event-details.html')


def edit_comment(request):
    return render(request, 'edit-comment.html')


def delete_comments(request):
    return render(request, 'delete-comments.html')


def login(request):
    return render(request, 'login.html')


def logout(request):
    return render(request, 'logout.html')


def confirm_logout(request):
    return render(request, 'confirm-logout.html')


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
    return render(request, 'register.html', {'form': form})
