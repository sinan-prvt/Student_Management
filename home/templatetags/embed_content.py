from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    """
    Convert YouTube URL into embeddable iframe.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    """
    video_id = None

    # long URL
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    if match:
        video_id = match.group(1)
    else:
        # short URL
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if match:
            video_id = match.group(1)

    if video_id:
        embed_code = f'<iframe width="100%" height="500" src="https://www.youtube.com/embed/{video_id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        return mark_safe(embed_code)

    return mark_safe('<p>Invalid YouTube URL</p>')

