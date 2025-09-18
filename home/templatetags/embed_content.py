from django import template
import re
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def youtube_embed(url):
    if not url:
        return ""
    if "youtu.be" in url:
        video_id = url.split("/")[-1]
    elif "youtube.com/watch?v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
    else:
        return url  # fallback to original URL
    return f"https://www.youtube.com/embed/{video_id}"


@register.simple_tag
def embed_pdf(url, width=800, height=600):
    """
    Embeds a PDF file in a responsive iframe.
    Usage: {% embed_pdf lesson.file.url 800 600 %}
    """
    if not url:
        return "No PDF available."

    html = f"""
    <div class="ratio ratio-4x3" style="max-width:{width}px; margin:auto;">
        <iframe src="{url}" width="{width}" height="{height}" style="border:1px solid #ccc;">
            This browser does not support PDFs. Please download the PDF to view it: 
            <a href="{url}" target="_blank">Download PDF</a>
        </iframe>
    </div>
    """
    return mark_safe(html)
