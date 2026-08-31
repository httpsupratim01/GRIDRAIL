FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
ARG VITE_DJANGO_API_URL=http://localhost:8000/api
ARG VITE_FASTAPI_URL=http://localhost:8001/api
ENV VITE_DJANGO_API_URL=$VITE_DJANGO_API_URL
ENV VITE_FASTAPI_URL=$VITE_FASTAPI_URL
RUN npm run build

FROM nginx:1.27-alpine

ENV PORT=80
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
