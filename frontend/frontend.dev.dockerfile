FROM node:20-slim as build

# Build the react app
WORKDIR /usr/src/app
COPY app/package.json app/package-lock.json ./
RUN npm install
COPY ./app . 

EXPOSE 3000