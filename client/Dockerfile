# ---- Base Node ----
FROM node:20-alpine AS base
WORKDIR /client
COPY package*.json ./

# ---- Dependencies ----
FROM base AS dependencies
RUN npm install

# ---- Build ----
FROM dependencies AS build
COPY . .
RUN npm run build

# ---- Release ----
FROM node:20-alpine AS release
WORKDIR /client
COPY --from=build /client .
RUN npm install --only=production
EXPOSE 3000
ENV NODE_ENV=production
CMD ["npm", "start"]