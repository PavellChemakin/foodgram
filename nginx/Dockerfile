FROM nginx:alpine

# Install curl just in case we need to probe the service during deploy.
RUN apk add --no-cache wget curl

# Copy the custom Nginx configuration into the container.  This file
# defines upstreams for the Django backend and React frontend and
# configures proxying and static/media file serving.  It will be
# placed as the default site configuration.
COPY nginx.conf /etc/nginx/conf.d/default.conf