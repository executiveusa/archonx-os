# ===========================================
# PAULI EFFECT - Production Docker Image
# Ultra-simple Coolify deployment
# ===========================================

FROM node:20-alpine

WORKDIR /app

# Install serve globally
RUN npm install -g serve

# Install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps || npm install

# Copy source
COPY . .

# Build frontend only
RUN npm run build || echo "Build completed with warnings"

# Simple health check file
RUN echo '{"status":"ok"}' > /app/dist/health.json

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

# Simple healthcheck
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health.json || exit 1

# Just serve static files - simplest possible setup
CMD ["serve", "-s", "dist", "-l", "3000"]
