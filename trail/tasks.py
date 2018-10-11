import io

from django.urls import reverse
from django.utils.translation import gettext as _
from staticmap import StaticMap, Line

from mountainbikers.celery import app
from .utils.gpx import get_coordinates, parse
from shell.utils.mail import mail


@app.task
def create_staticmaps(trail_id, base_uri):
    from .models import Trail
    current_trail = Trail.objects.get(pk=trail_id)

    try:
        static_thumbnail = StaticMap(425, 225, 10, 10, base_uri + '/trail/api/tile/{z}/{x}/{y}.png', tile_request_timeout=180)
        static_hero = StaticMap(1280, 480, 10, 10, base_uri + '/trail/api/tile/{z}/{x}/{y}.png', tile_request_timeout=180)

        for track in current_trail.tracks:
            coordinates = get_coordinates(track['points'])
            static_thumbnail.add_line(Line(coordinates, 'white', 11))
            static_hero.add_line(Line(coordinates, 'white', 11))

        for track in current_trail.tracks:
            coordinates = get_coordinates(track['points'])
            static_thumbnail.add_line(Line(coordinates, '#2E73B8', 5))
            static_hero.add_line(Line(coordinates, '#2E73B8', 5))

        image_thumbnail = static_thumbnail.render()
        image_hero = static_hero.render()

        file_thumbnail = io.BytesIO(b'')
        file_hero = io.BytesIO(b'')

        image_thumbnail.save(file_thumbnail, format='JPEG', optimize=True, progressive=True)
        image_hero.save(file_hero, format='JPEG', optimize=True, progressive=True)

        current_trail.thumbnail.delete(save=False)
        current_trail.thumbnail.save('thumbnail.jpg', file_thumbnail)

        current_trail.hero.delete(save=False)
        current_trail.hero.save('hero.jpg', file_hero)
    except:
        # TODO
        pass

    current_trail.is_draft = False
    current_trail.save()

    # TODO Translate
    to = mail(
        current_trail.name,
        'Your trail is ready.\n\n' +
        'https://mountainbikers.club' +
        reverse('trail__main', args=[current_trail.id])
    )
    to([current_trail.author.email])


@app.task
def parse_gpx(trail_id, base_uri):
    from .models import Trail

    trail = Trail.objects.get(pk=trail_id)

    if bool(trail.file):
        with trail.file.open() as file:
            gpx_file = file.read()
            name, description, tracks = parse(gpx_file.decode('utf-8'))

            first_track = tracks[0]

            trail.name = name or first_track['name'] or _('Unnamed trail')
            trail.description = description or first_track['description'] or ''
            trail.tracks = tracks
            trail.save()

            # Asynchronous Thumbnail
            create_staticmaps.delay(trail.id, base_uri)
