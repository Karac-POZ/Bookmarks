import redis
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from actions.utils import create_action

from .forms import ImageCreateForm
from .models import Image

# connect to redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
)


@login_required
def image_create(request):
    """
    View function to create a new image.
    It handles both GET and POST requests. When a GET request is made,
    it builds the form with data provided by the bookmarklet via GET.
    When a POST request is made, it validates the form data, saves the image
    and redirects to its detail view if the form data is valid.
    Args:
        request: The HTTP request object.
    Returns:
        A rendered HTML page.
    """
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # form data is valid
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # assign current user to the item
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            # redirect to new created image detail view
            return redirect(new_image.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = ImageCreateForm(data=request.GET)
    return render(
        request,
        'images/image/create.html',
        {'section': 'images', 'form': form},
    )


def image_detail(request, id, slug):
    """
    View function to display a single image detail page.
    It handles GET requests and increments the total image views and ranking.
    Args:
        request: The HTTP request object.
        id (int): The ID of the image.
        slug (str): The slug of the image.
    Returns:
        A rendered HTML page with the image details, including total views.
    """
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment total image views by 1
    total_views = r.incr(f'image:{image.id}:views')
    # increment image ranking by 1
    r.zincrby('image_ranking', 1, image.id)
    return render(
        request,
        'images/image/detail.html',
        {
            'section': 'images',
            'image': image,
            'total_views': total_views,
        },
    )


@login_required
@require_POST
def image_like(request):
    """
    View function to handle image likes.
    It handles POST requests and adds or removes a user from the image's likes list.
    Args:
        request: The HTTP request object.
    Returns:
        A JSON response with the status of the like operation.
    """
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            # Get the image object from the database
            image = Image.objects.get(id=image_id)
            # If the action is 'like', add the user to the image's likes list
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            # If the action is not 'like', remove the user from the image's likes list
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            # If the image does not exist, do nothing and return an error response
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    """
    View function to handle image list requests.
    It handles GET requests and returns a paginated list of images.
    Args:
        request: The HTTP request object.
    Returns:
        A rendered HTML page with the image list, or an empty response if requested via AJAX.
    """
    # Get all images from the database
    images = Image.objects.all()
    # Create a paginator to handle pagination of images
    paginator = Paginator(images, 8)
    # Get the current page number from the request
    page = request.GET.get('page')
    # Check if the request is for an AJAX image list only
    images_only = request.GET.get('images_only')

    try:
        # Try to get the requested page of images
        images = paginator.page(page)
    except PageNotAnInteger:
        # If the page number is not an integer, return the first page
        images = paginator.page(1)
    except EmptyPage:
        # If the requested page does not exist, handle it accordingly
        if images_only:
            # If the request is for an AJAX image list only, return an empty response
            return HttpResponse('')
        # Otherwise, return the last page of results
        images = paginator.page(paginator.num_pages)

    # Check if the request is for an AJAX image list only
    if images_only:
        # If so, render the image list template with only the requested images
        return render(
            request,
            'images/image/list_images.html',
            {'section': 'images', 'images': images}
        )
    else:
        # Otherwise, render the main image list template with all images and pagination
        return render(
            request,
            'images/image/list.html',
            {'section': 'images', 'images': images}
        )


@login_required
def image_ranking(request):
    """
    View function to handle image ranking requests.
    It retrieves the top 10 most viewed images from Redis and renders them on a page.
    Args:
        request: The HTTP request object.
    Returns:
        A rendered HTML page with the most viewed images.
    """
    # Get the top 10 most viewed images from Redis, ordered by their view count in descending order
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]

    # Extract the IDs of the most viewed images
    image_ranking_ids = [int(id) for id in image_ranking]

    # Get the actual Image objects from the database that correspond to the top 10 IDs
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))

    # Sort the most viewed images by their position in the Redis ranking, so they appear in order on the page
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))

    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed}
    )
