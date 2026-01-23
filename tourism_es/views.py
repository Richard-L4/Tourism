from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, ContactForm, CommentForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CardText, Comment, CommentReaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction


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
    card = get_object_or_404(CardText, id=pk)
    is_saved = False
    if request.user.is_authenticated:
        is_saved = card.saved_by.filter(pk=request.user.pk).exists()

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.card = card
            comment.save()
            return redirect('event-details', pk=card.pk)
    else:
        form = CommentForm()

    comments = card.comments.all().order_by('created_at')

    context = {
        'card': card,
        'comments': comments,
        'form': form,
        'is_saved': is_saved,
        'active_tab': 'event-details'
    }

    return render(request, 'event-details.html', context)


@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.user:
        return redirect('event-details', pk=comment.card.pk)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('event-details', pk=comment.card.pk)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'edit-comment.html',
                  {'form': form, 'comment': comment,
                   'active_tab': 'edit-comment'})


def delete_comments(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.user:
        return redirect('event-details', pk=comment.card.pk)

    if request.method == 'POST':
        card_pk = comment.card.pk
        comment.delete()
        return redirect('event-details', pk=card_pk)
    return render(request, 'delete-comments.html',
                  {'comment': comment, 'active_tab': 'delete-comments'})


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


@login_required
def toggle_reaction(request, comment_id, reaction_type):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    comment = get_object_or_404(Comment, id=comment_id)

    with transaction.atomic():
        existing = CommentReaction.objects.filter(user=request.user,
                                                  comment=comment).first()

        if existing:
            if existing.reaction != reaction_type:
                existing.reaction = reaction_type
                existing.save()
                status = 'changed'
            else:
                status = 'unchanged'
        else:
            CommentReaction.objects.create(user=request.user,
                                           comment=comment,
                                           reaction=reaction_type)
            status = 'added'

        likes_count = comment.reactions.filter(reaction='like').count()
        dislikes_count = comment.reactions.filter(reaction='dislike').count()

    return JsonResponse({'status': status, 'likes': likes_count,
                         'dislikes': dislikes_count})
