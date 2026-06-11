FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

# Install serve for production static file serving
RUN npm install -g serve

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["serve", "dist", "-l", "3000"]
