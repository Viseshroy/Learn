from django import template

register = template.Library()

@register.filter
def youtube_embed(value):
    """
    Converts YouTube watch or share links to embed links.
    """
    if 'youtube.com/watch?v=' in value:
        video_id = value.split('v=')[1].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtu.be/' in value:
        video_id = value.split('/')[-1].split('?')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    return value
