# Stage 1: Build the React Application
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependency files first (better caching)
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
# Ensure VITE_API_URL is set during build if needed, or handle at runtime
# ENV VITE_API_URL="http://<YOUR_NREC_IP>:8000" 
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Copy the build output from Stage 1 to Nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom Nginx config
COPY nginx.prod.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
