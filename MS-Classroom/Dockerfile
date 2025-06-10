FROM node:18-alpine

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./

RUN npm install --production

COPY prisma ./prisma/

RUN npx prisma generate

COPY . .

EXPOSE 3000

CMD ["node", "./index.js"]