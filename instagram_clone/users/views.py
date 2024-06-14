from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.db import transaction
from followers.models import Follower
from django.conf import settings
from posts.models import Post
from django.db.models import Q
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profile_pic = request.FILES.get('profile_pic')

        # Check if the user already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please log in.')
            return redirect('login')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(
                request, 'Username already exists. Please choose another one.')
            return redirect('register')

        # Create the user
        with transaction.atomic():
            CustomUser.objects.create_user(
                email=email,
                username=username,
                password=password,
                profile_pic=profile_pic
            )
        messages.success(
            request, 'Account created successfully. Please log in.')
        return redirect('login')
    
    storage = get_messages(request)
    for _ in storage:
        pass

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    storage = get_messages(request)
    for _ in storage:
        pass
    return render(request, 'login.html')


@login_required
def home_view(request):
    current_user = request.user
    users = CustomUser.objects.exclude(id=current_user.id)
    following = Follower.objects.filter(
        user_from=current_user).values_list('user_to_id', flat=True)
    print(following)
    
    # Only fetch posts from users that the current user follows
    all_user_posts = Post.objects.filter(user_id__in=following).order_by('-created_at')
    print(list(all_user_posts))

    context = {
        'users': users,
        'current_user': current_user,
        'following': following,
        'all_user_posts': all_user_posts,
        'current_user_id': current_user.id,

    }
    storage = get_messages(request)
    for _ in storage:
        pass
    return render(request, 'home.html', context)


@login_required
def view_user_profile(request, user_id):
    current_user = request.user
    user_following = Follower.objects.filter(user_from_id=user_id).count()
    user_followers = Follower.objects.filter(user_to_id=user_id).count()
    following = Follower.objects.filter(
        user_from=current_user).values_list('user_to_id', flat=True)
    user_profile = get_object_or_404(CustomUser, id=user_id)
    is_following = Follower.objects.filter(
        user_from=current_user, user_to=user_profile).exists()
    print(user_profile)
    user_posts = Post.objects.filter(user=user_profile)
    # user_posts_count = Post.objects.filter(user=user_profile)
    # other_users_posts = Post.objects.exclude(user=user_profile).order_by('-created_at')
    print(user_posts)
    print(user_following, user_followers)
    if is_following:
        user_posts = Post.objects.filter(
            user=user_profile).order_by('-created_at')
    else:
        user_posts = []
    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'current_user': request.user,
        'user_following': user_following,
        'user_followers': user_followers,
        'MEDIA_URL': settings.MEDIA_URL,
        'following': following,
        'user_posts': user_posts,
        'is_following': is_following,
        'posts_count': Post.objects.filter(user=user_profile).count(),
    })


@login_required
def view_profile(request):
    user_following = Follower.objects.filter(
        user_from_id=request.user.id).count()
    user_followers = Follower.objects.filter(
        user_to_id=request.user.id).count()
    user = get_object_or_404(CustomUser, id=request.user.id)
    user_posts = Post.objects.filter(user=user).order_by('-created_at')
    print(user_posts)
    print(user_following, user_followers)
    return render(request, 'profile.html', {'user_profile': request.user, 'user_following': user_following, 'user_followers': user_followers, 'MEDIA_URL': settings.MEDIA_URL, 'user_posts': user_posts, 'posts_count': user_posts.count()})


@login_required
def edit_profile(request):
    user_following = Follower.objects.filter(
        user_from_id=request.user.id).count()
    user_followers = Follower.objects.filter(
        user_to_id=request.user.id).count()
    if request.method == 'POST':
        # email = request.POST.get('email')
        username = request.POST.get('username')
        bio = request.POST.get('bio')
        profile_pic = request.FILES.get('profile_pic')

        user = request.user
        user.username = username
        user.bio = bio
        if profile_pic:
            user.profile_pic = profile_pic
        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'edit_profile.html', {'user': request.user, 'user_followers': user_followers, 'user_following': user_following})


def display_user_posts(request):
    print("inside display")
    user = get_object_or_404(CustomUser, id=request.user.id)
    user_posts = Post.objects.filter(user=user)
    print(user_posts)
    return render(request, 'profile.html', {'user_posts': user_posts, 'user': user})


def display_all_user_posts(request):
    print("inside display")
    user = get_object_or_404(CustomUser, id=request.user.id)
    all_user_posts = Post.objects.exclude(user=user)
    print(all_user_posts)
    return render(request, 'home.html', {'all_user_posts': all_user_posts, 'user': user})


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    if query:
        users = CustomUser.objects.filter(Q(username__icontains=query)).values(
            'id', 'username', 'first_name', 'last_name', 'profile_pic')
        return JsonResponse({'users': list(users)})
    return JsonResponse({'users': []})
