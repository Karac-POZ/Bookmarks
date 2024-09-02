from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from actions.models import Action
from actions.utils import create_action

from .forms import (
    LoginForm,
    ProfileEditForm,
    UserEditForm,
    UserRegistrationForm,
)
from .models import Contact, Profile

# Get the current user model
User = get_user_model()


def user_login(request):
    """
    Handles user login request.
    Args:
        request (HttpRequest): The incoming HTTP request.
    Returns:
        HttpResponse: A success message if login is successful.
                     Error messages otherwise.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    """
    Displays the user's dashboard.
    Args:
        request (HttpRequest): The incoming HTTP request.
    Returns:
        HttpResponse: The user's dashboard HTML.
    """
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related(
        'user', 'user__profile').prefetch_related('target')[:10]
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard', 'actions': actions}
    )


def register(request):
    """
    Handles user registration request.
    Args:
        request (HttpRequest): The incoming HTTP request.
    Returns:
        HttpResponse: A success message if registration is successful.
                     Error messages otherwise.
    """
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(
                request,
                'account/register_done.html',
                {'new_user': new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'account/register.html',
        {'user_form': user_form}
    )


@login_required
def edit(request):
    """
    Handles user profile edit request.
    Args:
        request (HttpRequest): The incoming HTTP request.
    Returns:
        HttpResponse: A success message if edit is successful.
                     Error messages otherwise.
    """
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'account/edit.html',
        {'user_form': user_form, 'profile_form': profile_form}
    )


@login_required
def user_list(request):
    """
    Lists all active users.
    Args:
        request (HttpRequest): The incoming HTTP request.
    Returns:
        HttpResponse: A list of all active users.
    """
    users = User.objects.filter(is_active=True)
    return render(
        request,
        'account/user/list.html',
        {'section': 'people', 'users': users}
    )


@login_required
def user_detail(request, username):
    """
    Displays a user's details.
    Args:
        request (HttpRequest): The incoming HTTP request.
        username (str): The username of the user to display.
    Returns:
        HttpResponse: The user's details HTML.
    """
    user = get_object_or_404(User, username=username, is_active=True)
    return render(
        request,
        'account/user/detail.html',
        {'section': 'people', 'user': user}
    )


@require_POST
@login_required
def user_follow(request):
    """
    Follows the specified user.
    Args:
        request (HttpRequest): The incoming HTTP request.
        username (str): The username of the user to follow.
    Returns:
        HttpResponse: A success message if following is successful.
                     Error messages otherwise.
    """
    username = request.POST.get('username')
    if username:
        user = get_object_or_404(User, username=username)
        if request.user != user:
            user.followers.add(request.user)
    return HttpResponse('User followed successfully')


@require_POST
@login_required
def user_unfollow(request):
    """
    Unfollows the specified user.
    Args:
        request (HttpRequest): The incoming HTTP request.
        username (str): The username of the user to unfollow.
    Returns:
        HttpResponse: A success message if unfollowing is successful.
                     Error messages otherwise.
    """
    username = request.POST.get('username')
    if username:
        user = get_object_or_404(User, username=username)
        if request.user != user:
            user.followers.remove(request.user)
    return HttpResponse('User unfollowed successfully')
