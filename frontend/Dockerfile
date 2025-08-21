FROM node:18

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

RUN npm install --global http-server

CMD [ "bash", "-lc", "rm -rf /static/* && cp -r /app/build/static/. /static/ && npx -y http-server -p 9000 /app/build" ]
