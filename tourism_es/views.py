from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, ContactForm, CommentForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CardText, Comment, CommentReaction, EventRating
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Avg

# ==============================
# Index / Home
# ==============================


def index(request):
    lang = request.GET.get('lang', 'en')

    valencia_intro = {
        'en': [
            "Valencia, on Spain’s east coast along the Mediterranean,"
            " blends rich history, stunning architecture,"
            " and a lively cultural scene.",
            "Its historic center features narrow streets, beautiful plazas,"
            " Valencia Cathedral, and the Silk Exchange."
            " Visitors enjoy ancient markets, local cuisine,"
            " and scenic strolls.",
            "The futuristic City of Arts and Sciences captivates "
            "all ages with an opera house, science museum, and aquarium."
            " Gardens, beaches, and parks offer relaxation,"
            " while festivals like Las Fallas showcase art, music, and fire.",
            "With tradition, modernity, and welcoming streets,"
            " Valencia provides a vibrant Mediterranean experience"
            " that delights the senses and leaves a lasting impression."
        ],
        'es': [
            "Valencia, en la costa este de España a lo largo del Mediterráneo",
            "combina rica historia, arquitectura impresionante y"
            " una vibrante escena cultural.",
            "Su centro histórico presenta calles estrechas, hermosas plazas,"
            " la Catedral de Valencia y la Lonja de la Seda."
            " Los visitantes disfrutan de mercados antiguos,"
            " gastronomía local "
            "y paseos escénicos.",
            "La futurista Ciudad de las Artes y las Ciencias cautiva a"
            " todas las edades con un teatro de ópera, museo de ciencias y"
            " acuario. Jardines, playas y parques ofrecen relajación,"
            " mientras que festivales como Las Fallas muestran arte,"
            " música y fuego.",
            "Con tradición, modernidad y calles acogedoras,"
            " Valencia ofrece una vibrante experiencia mediterránea"
            " que deleita los sentidos y deja una impresión duradera."
        ]
    }

    content_paragraphs = valencia_intro.get(lang, valencia_intro['en'])

    return render(request, 'index.html', {
        'active_tab': 'index',
        'content_paragraphs': content_paragraphs,
        'lang': lang
    })


# ==============================
# About / Contact Form
# ==============================
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


# ==============================
# Events Listing
# ==============================
def events(request):
    lang = request.GET.get('lang', 'en')
    card_texts = CardText.objects.all().order_by('id')

    for card in card_texts:
        translation = card.translations.filter(language=lang).first()
        card.translated_content = (
            translation.content
            if translation else card.content or 'Content coming soon.')

    paginator = Paginator(card_texts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events.html', {
        'active_tab': 'events',
        'page_obj': page_obj,
        'lang': lang
    })


# ==============================
# Event Details
# ==============================
def event_details(request, pk):
    card = get_object_or_404(CardText, id=pk)

    # 🌍 Language system (unchanged)
    lang = request.GET.get('lang', 'en')
    translation = card.translations.filter(language=lang).first()
    content = (
        translation.content
        if translation
        else card.content or 'Content coming soon.'
    )

    # ❤️ Saved events check (unchanged)
    is_saved = False
    if request.user.is_authenticated:
        is_saved = card.saved_by.filter(pk=request.user.pk).exists()

    # ⭐ HANDLE POST REQUESTS (NOW HANDLES TWO THINGS)
    if request.method == 'POST' and request.user.is_authenticated:

        # ⭐ --- RATING SUBMISSION ---
        if 'rating' in request.POST:
            rating_value = request.POST.get('rating')

            EventRating.objects.update_or_create(
                card=card,
                user=request.user,
                defaults={'rating': int(rating_value)}
            )

            return redirect('event-details', pk=card.pk)

        # 💬 --- COMMENT SUBMISSION ---
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.card = card
            comment.save()
            return redirect('event-details', pk=card.pk)

    else:
        form = CommentForm()

    # 💬 Comments list (unchanged)
    comments = card.comments.all().order_by('created_at')

    # ⭐ RATING STATS (NEW)
    average_rating = card.ratings.aggregate(avg=Avg('rating'))['avg']
    rating_count = card.ratings.count()

    # ⭐ User’s existing rating (NEW)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = EventRating.objects.filter(
            card=card, user=request.user).first()

    return render(request, 'event-details.html', {
        'card': card,
        'content': content,
        'comments': comments,
        'form': form,
        'is_saved': is_saved,
        'active_tab': 'event-details',
        'lang': lang,

        # ⭐ NEW CONTEXT FOR TEMPLATE
        'average_rating': average_rating,
        'rating_count': rating_count,
        'user_rating': user_rating,
    })


@login_required
def rate_card(request, pk):
    if request.method == 'POST':
        card = get_object_or_404(CardText, pk=pk)
        rating_value = int(request.POST.get('rating', 0))
        if rating_value < 1 or rating_value > 5:
            return JsonResponse({'error': 'Invalid rating'}, status=400)

        # Create/update user rating
        EventRating.objects.update_or_create(
            card=card,
            user=request.user,
            defaults={'rating': rating_value}
        )

        # Recalculate average and count
        avg = card.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        count = card.ratings.count()

        return JsonResponse({
            'rating': rating_value,
            'average_rating': round(avg, 1),
            'rating_count': count
        })
    return JsonResponse({'error': 'POST required'}, status=400)

# ==============================
# Comment Management
# ==============================


@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.user:
        return redirect('event-details', pk=comment.card.pk)

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('event-details', pk=comment.card.pk)

    return render(request,
                  'edit-comment.html',
                  {'form': form, 'comment': comment,
                   'active_tab': 'edit-comment'})


@login_required
def delete_comments(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if request.user != comment.user:
        return redirect('event-details', pk=comment.card.pk)

    if request.method == 'POST':
        card_pk = comment.card.pk
        comment.delete()
        return redirect('event-details', pk=card_pk)

    return render(request,
                  'delete-comments.html',
                  {'comment': comment, 'active_tab': 'delete-comments'})


# ==============================
# User Authentication
# ==============================
def user_login(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])
        if user:
            login(request, user)
            messages.success(request, f"You are logged in as {user.username}")
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html', {'active_tab': 'login', 'form': form})


def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return render(request, 'logout.html', {'active_tab': 'logout'})


def confirm_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    return render(request,
                  'confirm-logout.html', {'active_tab': 'confirm-logout'})


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(
            request, f"Account created for {user.username}! You can log in.")
        return redirect('login')

    return render(request, 'register.html', {'active_tab': 'register',
                                             'form': form})


# ==============================
# Comment Reactions (Like/Dislike)
# ==============================
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
            CommentReaction.objects.create(user=request.user, comment=comment,
                                           reaction=reaction_type)
            status = 'added'

        likes_count = comment.reactions.filter(reaction='like').count()
        dislikes_count = comment.reactions.filter(reaction='dislike').count()

    return JsonResponse({'status': status, 'likes': likes_count,
                        'dislikes': dislikes_count})
