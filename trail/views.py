import os
import requests

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.generic import DeleteView
from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.layouts import gridplot
from bokeh.models import Range1d, LinearAxis, PrintfTickFormatter, HoverTool

from .forms import GpxUploadForm, GpxEditForm
from .models import Trail
from .tasks import parse_gpx


@login_required
def new(request):
    current_user = request.user
    base_uri = request.scheme + '://' + request.get_host()

    if request.method == 'POST':
        form = GpxUploadForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            f = form.save(commit=False)
            f.author = current_user
            f.pub_date = timezone.now()
            f.save()
            parse_gpx.delay(f.id, base_uri)

            return HttpResponseRedirect(reverse('trail__main', args=[f.id]))

    else:
        form = GpxUploadForm()

    context = {
        'form': form,
    }

    return render(request, 'trail/new.html', context)


@login_required
def edit(request, trail_id):
    trail = get_object_or_404(Trail, pk=trail_id, author=request.user)

    if request.method == 'POST':
        form = GpxEditForm(data=request.POST, instance=trail)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('trail__main', args=[trail.id]))

    else:
        form = GpxEditForm(instance=trail)

    context = {
        'form': form,
        'trail': trail,
    }

    return render(request, 'trail/edit.html', context)


@login_required
def favorite(request, trail_id):
    current_user = request.user
    current_user_favorite_trails = current_user.favorite_trails.all()
    trail = get_object_or_404(Trail, pk=trail_id)

    if trail in current_user_favorite_trails:
        current_user.favorite_trails.remove(trail)
    else:
        current_user.favorite_trails.add(trail)

    return HttpResponseRedirect(reverse('trail__main', args=[trail.id]))


class TrailDelete(DeleteView):
    success_url = reverse_lazy('dashboard__main')
    model = Trail

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)


def main(request, trail_id):
    current_user = request.user
    trail = get_object_or_404(Trail, pk=trail_id)
    is_favorite = False
    charts = []

    if trail.is_private and not (current_user.is_authenticated and trail.author == current_user):
        raise Http404(_('Trail does not exist'))

    if current_user.is_authenticated:
        is_favorite = current_user in trail.favorite_by.all()

    # Chart
    # TODO Slope
    if trail.tracks is not None and len(trail.tracks) > 0:
        for track in trail.tracks:
            x_distance = list(map(lambda p: p['total_distance'], track['points']))
            y_elevation = list(map(lambda p: p['elevation'], track['points']))
            y_speed = list(map(lambda p: p['speed'], track['points']))
            y_heart_rate = list(map(lambda p: p['heart_rate'], track['points']))
            y_temperature = list(map(lambda p: p['temperature'], track['points']))
            y_cadence = list(map(lambda p: p['cadence'], track['points']))

            source = ColumnDataSource(data=dict(
                distance=x_distance,
                elevation=y_elevation,
                speed=y_speed,
                heart_rate=y_heart_rate,
                temperature=y_temperature,
                cadence=y_cadence
            ))

            tools = 'xpan,xzoom_in,xzoom_out,reset,crosshair'

            main_plot = figure(
                tools=tools,
                sizing_mode='scale_width',
                plot_width=1100,
                plot_height=290,
            )

            temp_plot = figure(
                tools=tools,
                sizing_mode='scale_width',
                plot_width=1100,
                plot_height=170,
            )

            main_plot.x_range = Range1d(start=0, end=x_distance[-1])
            main_plot.y_range = Range1d(start=min(y_elevation) - 30, end=max(y_elevation) + 100)

            temp_plot.x_range = main_plot.x_range
            temp_plot.y_range = Range1d(start=min(y_elevation) - 30, end=max(y_elevation) + 100)

            elevation_line = main_plot.line('distance', 'elevation', source=source, line_width=1, color='#3d85cc', alpha=0.85)
            temp_plot.line('distance', 'elevation', source=source, line_width=1, color='#3d85cc', alpha=0.85)

            end_patch = min(y_elevation) - 30
            x_patch = [x_distance[0]] + x_distance + [x_distance[-1]]
            y_patch = [end_patch] + y_elevation + [end_patch]
            main_plot.patch(x_patch, y_patch, legend=_('Elevation'), color='#3d85cc', alpha=0.8)

            main_plot.xaxis[0].formatter = PrintfTickFormatter(format='%4.1f km')
            temp_plot.xaxis[0].formatter = PrintfTickFormatter(format='%4.1f km')

            main_plot.yaxis[0].formatter = PrintfTickFormatter(format='%5d m')
            main_plot.yaxis[0].major_label_text_color = '#3d85cc'
            temp_plot.yaxis[0].visible = False

            tooltips = [
               # ('distance', '@distance{%4.2f km}'),
               ('elevation', '@elevation{%5d m}'),
            ]

            y_index = 1

            if max(y_speed) > 0:
                main_plot.extra_y_ranges['speed'] = Range1d(start=min(y_speed), end=max(y_speed) + 5)
                main_plot.add_layout(LinearAxis(y_range_name='speed'), 'left')
                # y_patch = [0.] + y_speed + [0.]
                # main_plot.patch(x_patch, y_patch, y_range_name='speed', legend=_('Speed'), color='#66cc66', alpha=0.5)
                main_plot.line('distance', 'speed', source=source, y_range_name='speed',
                               legend=_('Speed'), line_width=2, color='#66cc66', alpha=0.7)
                main_plot.yaxis[y_index].formatter = PrintfTickFormatter(format='%3d km/h')
                main_plot.yaxis[y_index].major_label_text_color = '#66cc66'
                tooltips.append(('speed', '@speed{%3.1f km/h}'))
                y_index = y_index + 1

            if max(y_heart_rate) > 0:
                main_plot.extra_y_ranges['heart_rate'] = Range1d(start=min(y_heart_rate) - 10, end=max(y_heart_rate) + 10)
                main_plot.add_layout(LinearAxis(y_range_name='heart_rate'), 'right')
                main_plot.line('distance', 'heart_rate', source=source, y_range_name='heart_rate', legend=_('Heart rate'), line_width=2, color='#f2777a', alpha=0.7)
                main_plot.yaxis[y_index].formatter = PrintfTickFormatter(format='%3d bpm')
                main_plot.yaxis[y_index].major_label_text_color = '#f2777a'
                tooltips.append(('heart_rate', '@heart_rate{%3d bpm}'))

            if max(y_cadence) > 0:
                main_plot.extra_y_ranges['cadence'] = Range1d(start=min(y_cadence) - 10, end=max(y_cadence) + 10)
                main_plot.add_layout(LinearAxis(y_range_name='cadence'), 'right')
                main_plot.line('distance', 'cadence', source=source, y_range_name='cadence',
                               legend=_('Cadence'), line_width=2, color='#cc99cc', alpha=0.7)
                main_plot.yaxis[y_index].formatter = PrintfTickFormatter(format='%3d')
                main_plot.yaxis[y_index].major_label_text_color = '#cc99cc'
                tooltips.append(('cadence', '@cadence{%3d}'))

            if max(y_temperature) > 0:
                temp_plot.extra_y_ranges['temperature'] = Range1d(start=min(y_temperature) - 3, end=max(y_temperature) + 3)
                temp_plot.add_layout(LinearAxis(y_range_name='temperature'), 'left')
                temp_plot.line('distance', 'temperature', source=source, y_range_name='temperature', legend=_('Temperature'), line_width=2, color='#ffcc66')
                temp_plot.yaxis[1].formatter = PrintfTickFormatter(format='%2d °C')
                temp_plot.yaxis[1].major_label_text_color = '#ffcc66'
                tooltips.append(('temperature', '@temperature{%2d °C}'))

            # Tools
            hover_tool = HoverTool(
                renderers=[elevation_line],
                tooltips=tooltips,
                formatters={
                    'distance': 'printf',
                    'elevation': 'printf',
                    'speed': 'printf',
                    'heart_rate': 'printf',
                    'cadence': 'printf',
                    'temperature': 'printf',
                },
                mode='vline'
            )
            main_plot.add_tools(hover_tool)

            # Generic styling
            # http://bokeh.pydata.org/en/latest/docs/user_guide/styling.html
            def set_plot_styles(plot):
                plot.border_fill_color = '#2d2d2d'
                plot.background_fill_color = '#393939'
                plot.outline_line_color = 'black'

                plot.xaxis.major_label_text_color = '#d3d0c8'
                plot.xaxis.major_label_text_font = 'UniNeue'
                plot.yaxis.major_label_text_font = 'UniNeue'

                plot.xgrid.grid_line_color = '#515151'
                plot.xgrid.grid_line_dash = [6, 4]
                plot.ygrid.grid_line_color = '#515151'
                plot.ygrid.grid_line_dash = [6, 4]

                plot.xgrid.minor_grid_line_color = '#515151'
                plot.xgrid.minor_grid_line_alpha = 0.5
                plot.xgrid.minor_grid_line_dash = [6, 4]
                plot.ygrid.minor_grid_line_color = '#515151'
                plot.ygrid.minor_grid_line_alpha = 0.5
                plot.ygrid.minor_grid_line_dash = [6, 4]

                plot.title.text_color = '#a09f93'

                plot.legend.location = 'top_left'
                plot.legend.label_text_font = "UniNeue"
                plot.legend.label_text_color = '#a09f93'
                plot.legend.border_line_color = '#515151'
                plot.legend.background_fill_color = '#2d2d2d'
                plot.legend.background_fill_alpha = 0.85
                plot.legend.click_policy = 'hide'
                plot.legend.inactive_fill_color = '#2d2d2d'

            set_plot_styles(main_plot)
            set_plot_styles(temp_plot)

            grid = gridplot([[main_plot], [temp_plot]], sizing_mode='scale_width', toolbar_location='above')

            script, div = components(grid)

            charts.append({
                'script': script,
                'div': div,
            })

    context = {
        'trail': trail,
        'is_favorite': is_favorite,
        'charts': charts,
    }

    return render(request, 'trail/main.html', context)


def track_json(request, trail_id, track_id):
    current_user = request.user
    trail = get_object_or_404(Trail, pk=trail_id)

    if trail.is_private and not (current_user.is_authenticated and trail.author == current_user):
        raise Http404(_('Trail does not exist'))

    try:
        points = trail.tracks[track_id] or {}
    except IndexError:
        raise Http404(_('Track index is out of range'))

    return JsonResponse(points, safe=False)


def tile(request, z, x, y):
    url_komoot = 'http://a.tile.komoot.de/komoot-2/{}/{}/{}.png'.format(z, x, y)
    url_topo = 'https://b.tile.opentopomap.org/{}/{}/{}.png'.format(z, x, y)
    url_cycle = 'https://tile.thunderforest.com/cycle/{}/{}/{}.png?apikey={}'\
        .format(z, x, y, os.environ.get('OPEN_CYCLE_MAP'))

    r = requests.get(url_komoot, timeout=60)
    if r.status_code != 200:
        r = requests.get(url_topo, timeout=60)
    if r.status_code != 200:
        r = requests.get(url_cycle, timeout=60)

    content = r.content if r.status_code == 200 else None

    return HttpResponse(content, content_type='image/png')
