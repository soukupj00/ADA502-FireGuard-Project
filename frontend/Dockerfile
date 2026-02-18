# STAGE 1: Base (Used by both Dev and Prod)
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
# Use 'npm ci' for reliable installs
RUN npm ci

# STAGE 2: Development (Target this for local dev)
FROM base AS development
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# STAGE 3: Build (Intermediate step for Prod)
FROM base AS builder
COPY . .
RUN npm run build

# STAGE 4: Production (Target this for NREC/Prod)
FROM nginx:alpine AS production
# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom Nginx config
COPY nginx.prod.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]