# === OpenClaw Workday Agent ===
# Zero-install container for running automation scripts.
#
# Build:  docker build -t openclaw-workday-agent .
# Run:    docker run --rm --env-file .env openclaw-workday-agent node scripts/approve-workday.js

FROM node:20-alpine

WORKDIR /app

# Install dependencies first (layer caching)
COPY package.json package-lock.json ./
RUN npm ci --production

# Copy scripts
COPY scripts/ scripts/

# Non-root user for security
RUN addgroup -S agent && adduser -S agent -G agent
USER agent

# Default: print usage
CMD ["node", "-e", "console.log('Usage: docker run --rm --env-file .env openclaw-workday-agent node scripts/<script>.js')"]
