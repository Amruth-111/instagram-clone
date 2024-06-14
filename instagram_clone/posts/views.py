from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST, require_GET,require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post,  Comment
# from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.contrib import messages
import json
import logging

User = get_user_model()


@login_required
def view_post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    print("inside view post details")
    user_profile = post.user
    is_own_post = (post.user == request.user)
    comment_count = post.comments.filter().count()
    return render(request, 'post_details.html', {
        'post': post,
        'user_profile': user_profile,
        'is_own_post': is_own_post,
        'comment_count': comment_count,
        'current_user_id':request.user.id,
    })


@login_required
def add_post(request):
    if request.method == 'POST':
        user = request.user
        caption = request.POST.get('caption')
        image_file = request.FILES.get('image')
        str_user = str(user)
        print(str_user)
        if caption and image_file:
            post = Post.objects.create(
                user=user, caption=caption, image=image_file)

            post_details = {
                "post_url": post.image.url,
                "post_caption": post.caption,
            }
            return JsonResponse({"message": "Post added successfully", "post_details": post_details, "success": True, "user": str_user})
        else:
            return JsonResponse({"error": "Caption and image file are required", "success": False}, status=400)

    return JsonResponse({"error": "Method not allowed", "success": False}, status=405)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    print("inside edit posts")
    if request.method == 'POST':
        new_caption = request.POST.get('caption')
        post.caption = new_caption
        post.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'fail'})


@login_required
def delete_post(request, post_id):
    print("inside delete")
    user_id = request.user.id
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.delete()
        # messages.success(request, "Post deleted successfully.")
        return JsonResponse({'status': 'success'})
    else:
        # messages.error(request, "Failed to delete the post.")
        return JsonResponse({'status': 'fail'})


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if post.likes.filter(id=user.id).exists():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    liked_users = list(post.likes.values_list('username', flat=True))
    return JsonResponse({'liked': liked, 'total_likes': post.total_likes, 'liked_users': liked_users})


logger = logging.getLogger(__name__)


@login_required
@require_POST
# def add_comment(request, post_id):
#     if request.method == "POST":
#         try:
#             user = request.user
#             post = get_object_or_404(Post, id=post_id)
#             data = json.loads(request.body)

#             logger.debug(f"Received data: {data}")

#             text = data.get('text', '').strip()
#             logger.debug(f"Comment text: {text}")

#             parent_id = data.get('parent_id')
#             parent = None
#             if parent_id:
#                 parent = get_object_or_404(Comment, id=parent_id)

#             if not text:
#                 logger.error("Comment text cannot be empty")
#                 return JsonResponse({"success": False, "error": "Comment text cannot be empty"})

#             comment = Comment.objects.create(
#                 user=user, post=post, text=text, parent=parent)
#             return JsonResponse({"success": True, "comment": comment.id})
#         except Exception as e:
#             logger.exception("Error while adding comment")
#             return JsonResponse({"success": False, "error": str(e)})
#     return JsonResponse({"success": False, "error": "Invalid request"})

def add_comment(request, post_id):
    try:
        user = request.user
        post = get_object_or_404(Post, id=post_id)
        data = json.loads(request.body)
        
        text = data.get('text', '').strip()
        parent_id = data.get('parent_id')
        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
        
        if not text:
            return JsonResponse({"success": False, "error": "Comment text cannot be empty"})

        comment = Comment.objects.create(user=user, post=post, text=text, parent=parent)
        return JsonResponse({"success": True, "comment": comment.id})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    

@login_required
@require_GET
def get_comments(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.filter(parent__isnull=True).values(
        'id', 'user__username', 'text', 'created_at','user_id')
    return JsonResponse({'comments': list(comments)})


@login_required
@require_GET
# def get_replies(request, comment_id):
#     comment = Comment.objects.get(id=comment_id)
#     replies = comment.replies.values(
#         'id', 'user__username', 'text', 'created_at')
#     return JsonResponse({'replies': list(replies)})
def get_replies(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    replies = comment.replies.values('id', 'user__username', 'text', 'created_at', 'post_id','user_id')
    return JsonResponse({'replies': list(replies)})


@require_http_methods(["DELETE"])
@login_required
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
        comment.delete()
        return JsonResponse({'success': True})
    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment not found or you do not have permission to delete it'})
