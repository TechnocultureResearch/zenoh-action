FROM node:16-alpine AS development
ENV NODE_ENV development
RUN npm install -g pnpm

WORKDIR /dashboard

COPY package.json .
COPY package-lock.json .
RUN pnpm install

COPY . .

EXPOSE 3000

CMD [ "pnpm", "start" ]
