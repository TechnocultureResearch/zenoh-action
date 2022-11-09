FROM node:16-alpine AS development
ENV NODE_ENV development

WORKDIR /dashboard

COPY package.json yarn.lock .
RUN yarn install --pure-lockfile

COPY . .

EXPOSE 3000

CMD [ "yarn", "start" ]
