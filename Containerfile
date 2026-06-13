FROM caddy:alpine

COPY index.html /usr/share/caddy/index.html
COPY styles.css /usr/share/caddy/styles.css
COPY app.js /usr/share/caddy/app.js
COPY facts.json /usr/share/caddy/facts.json
COPY country-codes.json /usr/share/caddy/country-codes.json
COPY assets/ /usr/share/caddy/assets/

EXPOSE 80