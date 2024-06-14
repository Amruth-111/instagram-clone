from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Follower, CustomUser


@login_required
def follow_user(request, user_id):
    if request.method == 'POST':
        user_to_follow = get_object_or_404(CustomUser, id=user_id)
        if request.user != user_to_follow:
            follow_instance, created = Follower.objects.get_or_create(
                user_from=request.user, user_to=user_to_follow)
            if not created:
                return JsonResponse({'message': 'You are already following this user', 'success': 'false'}, status=400)
            return JsonResponse({'message': 'User followed successfully', 'success': 'true'}, status=201)
        else:
            return JsonResponse({'message': 'You cannot follow yourself', 'success': 'false'}, status=400)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)


@login_required
def unfollow_user(request, user_id):
    if request.method == 'POST':
        user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
        follow_instance = Follower.objects.filter(
            user_from=request.user, user_to=user_to_unfollow).first()
        if follow_instance:
            follow_instance.delete()
            return JsonResponse({'message': 'User unfollowed successfully', 'success': 'true'}, status=200)
        else:
            return JsonResponse({'message': 'You are not following this user', 'success': 'false'}, status=400)
    else:
        return JsonResponse({'message': 'Method not allowed', 'success': 'false'}, status=405)


@login_required
def followers_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    followers = Follower.objects.filter(user_to=user).select_related('user_from').values(
        'user_from__id', 'user_from__username', 'user_from__profile_pic'
    )
    print(followers)
    return JsonResponse({'followers': list(followers)})


@login_required
def following_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    following = Follower.objects.filter(user_from=user).select_related('user_to').values(
        'user_to__id', 'user_to__username', 'user_to__profile_pic'
    )
    print(following)
    return JsonResponse({'following': list(following)})
