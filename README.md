# Mountain Bikers Club
## Technologies
- The application runs with Django and PostgreSQL.
- The maps are build with Leaflet.
- The JavaScript is built on top of [my JS library](https://www.cedeber.fr), which is open source too.

## Browsers support
I am not going to do Progressive enhancement. Mountain Bikers Club is a side project and nearly all modern browsers offer the support of what is needed:
- CSS variables
- CSS Grid
- ES 2017 support at minimun, as the app is loaded as an ES Module, which includes all API released before ES 2017.
- Web Component and Shadow DOM (later this year with Firefox 63)

## Hosting
- The website and the database are hosted on Heroku.
- The user's files (GPX, photos, ...) are uploaded and served via Amazon Web Service S3.
- The DNS is managed on Cloudflare.
- The map tiles come from OpenTopoMap.

## Privacy
When I started to code websites in 1998, we were used to listen to people's feedbacks. This is the web I love.
I am not going to install any script that do statistics.

# Support
The hosting on Heroku and AWS S3 are not free and I code this app during my free time. Having ads on the website is not an option. If you want to support the development of the app, you can send me some money via Buy Me A Coffee.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cedeber)
