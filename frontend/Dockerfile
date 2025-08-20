FROM node:18

WORKDIR /app

# Install dependencies based on the package definitions.  Using
# `npm ci` ensures a reproducible build defined by package-lock.json.
COPY package.json package-lock.json ./
RUN npm ci

# Copy the remainder of the application source into the container and
# compile a production build of the React SPA.  The build output
# resides in the `build` directory.
COPY . .
RUN npm run build

# Install a lightweight HTTP server to serve the compiled static
# assets.  This step is separate from the build to ensure that
# `http-server` isn’t added to the project dependencies.  It will
# serve files from the `build` directory.
RUN npm install --global http-server

# On container start, copy the compiled static assets into the shared
# `/static` volume and then launch the HTTP server on port 9000.
CMD [ "bash", "-lc", "rm -rf /static/* && cp -r /app/build/static/. /static/ && npx -y http-server -p 9000 /app/build" ]