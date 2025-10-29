# --- Build Stage ---
FROM node:20-alpine AS build
WORKDIR /app

# Enable corepack for pnpm
RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

# --- Runtime Stage ---
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

# Optional SPA fallback (uncomment to enable history API fallback)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


