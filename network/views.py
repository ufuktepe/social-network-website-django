import json
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import JsonResponse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Profile

# Number of posts to be displayed on each page
NUM_OF_POSTS_ON_PAGE = 10


class NewPostForm(ModelForm):
    """
    ModelForm for creating a new post.
    """
    class Meta:
        model = Post
        fields = ["content"]
        # Remove the "content" label
        labels = {"content": ""}

        widgets = {
            'content': forms.Textarea(attrs={
                'style': 'width:100%'}),
        }


def index(request):
    """
    Default route that returns all posts.
    """
    # Paginate all posts
    page = paginate(request, Post.objects.all())
    return render(request, "network/index.html", {"page": page, "new_post_form": NewPostForm(), "display_profile": False,
                                                  "all_users": None, "following": None, "followers": None})


def login_view(request):
    """
    Verifies user credentials and logs in the user.
    """
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    """
    Logs out the user.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Creates a new user and logs in the user.
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            new_profile = Profile(user=user)
            new_profile.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def create_post(request):
    """
    Creates new post. Then redirects to the index page.
    """
    if request.method == "POST":

        # Fetch the new post form
        new_post_form = NewPostForm(request.POST)

        # Check if the new post form is valid
        if new_post_form.is_valid():
            # Get the content and create a new Post object
            content = new_post_form.cleaned_data["content"]
            new_post = Post(author=request.user, content=content)
            new_post.save()

            # Redirect to the listing page
            return HttpResponseRedirect(reverse("index"))

        else:
            # If the new post form is invalid then render the index page with new_post_form
            page = paginate(request, Post.objects.all())
            return render(request, "network/index.html", {"page": page, "new_post_form": new_post_form,
                                                          "display_profile": False, "all_users": None,
                                                          "following": None, "followers": None})

    # If request is not a post request, redirect to the index page
    return HttpResponseRedirect(reverse("index"))


def edit_post(request, post_id):
    """
    Edits an existing post. Then returns the serialized data of the post object.
    """
    if request.method == "PUT":
        # Get the post object based on post_id
        post = Post.objects.get(pk=post_id)
        # Parse the JSON string and convert it into a dictionary
        data = json.loads(request.body)
        if data.get("content") is not None:
            # Update the post content
            post.content = data["content"]
        post.save()

        # Return updated content
        return JsonResponse({"content": post.content})

    # Edit post must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


def switch_like(request, post_id):
    """
    Switches the like/unlike state of a post for the current user.
    If the current user exists in user_likes of the post then it removes the current user from user_likes.
    Otherwise, it adds the current user to the user_likes.
    Returns the updated number of likes of the post and a boolean value (flag) to indicate whether the current
    user liked or unliked the post.
    """
    if request.method == "PUT":
        # Get the post object based on post_id
        post = Post.objects.get(pk=post_id)
        flag = True
        if request.user in post.user_likes.all():
            # Unlike
            post.user_likes.remove(request.user)
            flag = False
        else:
            # Like
            post.user_likes.add(request.user)
        post.save()

        # Return the number of likes and the boolean value indicating liked/unliked
        return JsonResponse({"num_of_likes": len(post.user_likes.all()), "flag": flag})

    # Like/Unlike must be via PUT
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


def display_profile(request, user_id):
    """
    Displays all of the posts for the current user, in reverse chronological order.
    Also, displays the number of followers the user has, as well as the number of people that the user follows.
    Additionally, returns the signed in users.
    """
    # Get all users except the current user
    all_users = User.objects.exclude(pk=user_id).all()

    # Try to get the users that the current user follows and the followers of the user
    try:
        following = Profile.objects.get(user=request.user).following.all()
        followers = request.user.followers
    # If there is no profile associated with the current user, create a profile for the user
    except Profile.DoesNotExist:
        new_profile = Profile(user=request.user)
        new_profile.save()
        following = None
        followers = None

    # Paginate all posts of the current user
    page = paginate(request, Post.objects.filter(author=request.user))

    # Render the index page with all posts of the current user, all_users, following, and followers
    return render(request, "network/index.html", {"page": page, "new_post_form": None, "display_profile": True,
                                                  "all_users": all_users, "following": following,
                                                  "followers": followers})


def switch_follow(request, other_user_id):
    """
    Switches the follow/unfollow state of a current user for another user.
    If the current user exists in the following list of the other user, then it removes the current user from the
    following list.
    Otherwise, it adds the current user to the following list.
    Redirects to profile page.
    """
    # Get the other user object
    other_user = User.objects.get(pk=other_user_id)
    if Profile.objects.filter(user=request.user, following=other_user).exists():
        # Unfollow
        Profile.objects.get(user=request.user).following.remove(other_user)
    else:
        # Follow
        Profile.objects.get(user=request.user).following.add(other_user)

    # Redirects to the profile page
    return HttpResponseRedirect(reverse("display_profile", args=(request.user.id,)))


def display_following(request):
    """
    Displays a page which has all posts made by users that the current user follows.
    """
    # Try to get the users that the current user follows
    try:
        following = Profile.objects.get(user=request.user).following.all()
    # If there is no profile associated with the current user, create a profile for the current user
    except Profile.DoesNotExist:
        new_profile = Profile(user=request.user)
        new_profile.save()
        following = None

    # Paginate all posts made by users that the current user follows
    page = paginate(request, Post.objects.filter(author__in=following))

    # Render the index page with all posts made by users that the current user follows
    return render(request, "network/index.html", {"page": page, "new_post_form": None, "display_profile": False,
                                                  "all_users": None, "following": None, "followers": None})


def paginate(request, posts):
    """
    Splits posts across several pages based on the value of NUM_OF_POSTS_ON_PAGE
    Returns the posts on the requested page
    """
    # Get the page number of the requested page
    page_num = request.GET.get('page', 1)
    # Create Paginator object
    paginator = Paginator(posts, NUM_OF_POSTS_ON_PAGE)
    # Return the posts on the requested page
    return paginator.page(page_num)

