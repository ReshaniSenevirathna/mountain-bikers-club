# Mountain Bikers Club
## Technologies
- The application runs with Django, Celery, PostgreSQL and Redis.
- The maps are build with Leaflet and OpenStreetMap.
- The graphs are build thanks to Bokeh.
- The JavaScript and CSS are built on top of [my frontend library](https://github.com/cedeber/frontend-library).

## Browsers support
Mountain Bikers Club doesn't support legacy browsers.

These are the minimun requirements (JavaScript is not mandatory):
- CSS variables
- CSS Grid
- ES 2017 support at minimun, as the app is loaded as an ES Module,
  which includes all API released before ES 2017.
- Web Component and Shadow DOM

## Hosting
- The website and the databases are hosted on Heroku.
- The user's files are uploaded and served via Digital Ocean Spaces.
- The DNS and the SSL certificate are managed through Cloudflare.
- The map tiles come from Komoot, OpenTopoMap and OpenCycleMap.

## Privacy
When I started to code websites in '98, we were used to listen to people's feedbacks.
This is the web I love. I am not going to install any script that do neither
statistics nor ads. As you may have noticed there is no Cookie banner.
It's not a mistake!

## Stay In Touch
- [Mastodon](https://mastodon.social/@cedeber)
- [Facebook](https://fb.me/mountainbikersclub)

## Contribution

Please make sure to read the [Contributing Guide](CONTRIBUTING.md) before making
a pull request.

Thank you to all [the people who already contributed to Mountain Bikers Club](https://github.com/cedeber/mountain-bikers-club/graphs/contributors)!

## Financial Contribution
The hosting on Heroku and Digital Ocean are not free. If you want to support the development
of the app, you can send me some money via Buy Me A Coffee.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cedeber)


## License

[GPL-3.0](LICENSE)

Copyright (c) 2018, Cédric Eberhardt
