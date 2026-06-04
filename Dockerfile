# Single-service deploy (Railway): build the React web, then serve it from FastAPI.
# Web env (VITE_*) is baked at build time -> pass as build args (Railway provides them).

# --- stage 1: build the web ---
FROM node:20-slim AS web
WORKDIR /web
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
ARG VITE_API_BASE_URL=""
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY
RUN npm run build

# --- stage 2: api runtime (serves the web) ---
FROM python:3.12-slim AS api
WORKDIR /app
COPY apps/api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/ ./
COPY --from=web /web/dist ./web
ENV WEB_DIR=/app/web \
    APP_ENV=production
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
