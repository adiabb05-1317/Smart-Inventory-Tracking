# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Enable corepack for pnpm
RUN corepack enable

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Accept build args for Vite env
ARG VITE_BACKEND_URL=""
ARG VITE_API_PREFIX="/api"

# Set envs for build (baked into bundle)
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL
ENV VITE_API_PREFIX=$VITE_API_PREFIX

# Build for production with env
RUN echo "Building with VITE_BACKEND_URL=$VITE_BACKEND_URL VITE_API_PREFIX=$VITE_API_PREFIX" && pnpm build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
