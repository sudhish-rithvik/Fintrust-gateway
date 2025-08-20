# Stage 1: Build the React app
FROM node:20-alpine as build

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve with NGINX
FROM nginx:alpine

# Copy build output to NGINX html directory
COPY --from=build /app/build /usr/share/nginx/html

# Replace default NGINX config (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
