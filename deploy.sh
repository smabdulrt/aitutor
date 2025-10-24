#!/bin/bash

# Configuration
PROJECT_ID="aitutor-473420"
REGION="us-central1"

# Check environment argument
ENV=${1:-staging}  # Default to staging if no argument provided

if [ "$ENV" != "staging" ] && [ "$ENV" != "prod" ]; then
    echo "❌ Invalid environment. Use 'staging' or 'prod'"
    echo "Usage: ./deploy.sh [staging|prod]"
    exit 1
fi

# Get API key from environment variable
if [ -z "$VITE_GEMINI_API_KEY" ]; then
    echo "⚠️  VITE_GEMINI_API_KEY environment variable not set"
    echo "Please set it: export VITE_GEMINI_API_KEY=your-api-key"
    exit 1
fi

echo "🚀 Deploying to Google Cloud Run - $ENV environment"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Set environment-specific variables
if [ "$ENV" = "staging" ]; then
    echo "📦 Deploying STAGING environment..."
    CONFIG_FILE="cloudbuild-staging.yaml"
    
    # These will be set after first deployment
    DASH_API_URL="https://dash-api-staging-594749838895.us-central1.run.app"
    SHERLOCKED_API_URL="https://sherlocked-api-staging-594749838895.us-central1.run.app"
    MEDIAMIXER_URL="https://mediamixer-staging-594749838895.us-central1.run.app"
    
    SERVICE_SUFFIX="-staging"
else
    echo "📦 Deploying PRODUCTION environment..."
    CONFIG_FILE="cloudbuild-prod.yaml"
    
    DASH_API_URL="https://dash-api-utmfhquz6a-uc.a.run.app"
    SHERLOCKED_API_URL="https://sherlocked-api-utmfhquz6a-uc.a.run.app"
    MEDIAMIXER_URL="https://mediamixer-utmfhquz6a-uc.a.run.app"
    
    SERVICE_SUFFIX=""
fi

# Convert HTTPS to WSS for WebSocket URLs
MEDIAMIXER_WS_URL=$(echo $MEDIAMIXER_URL | sed 's/https/wss/')

echo "🔗 Using URLs:"
echo "  DASH API: $DASH_API_URL"
echo "  SherlockED: $SHERLOCKED_API_URL"
echo "  MediaMixer: $MEDIAMIXER_URL"
echo ""

# Submit build with substitutions
gcloud builds submit \
  --config=$CONFIG_FILE \
  --substitutions=_VITE_GEMINI_API_KEY="$VITE_GEMINI_API_KEY",_DASH_API_URL="$DASH_API_URL",_SHERLOCKED_API_URL="$SHERLOCKED_API_URL",_MEDIAMIXER_COMMAND_WS="${MEDIAMIXER_WS_URL}/command",_MEDIAMIXER_VIDEO_WS="${MEDIAMIXER_WS_URL}/video" \
  .

# Get actual deployed URLs
echo ""
echo "🔍 Retrieving service URLs..."

DASH_URL=$(gcloud run services describe dash-api$SERVICE_SUFFIX --region $REGION --format 'value(status.url)' 2>/dev/null)
SHERLOCKED_URL=$(gcloud run services describe sherlocked-api$SERVICE_SUFFIX --region $REGION --format 'value(status.url)' 2>/dev/null)
MEDIAMIXER_URL=$(gcloud run services describe mediamixer$SERVICE_SUFFIX --region $REGION --format 'value(status.url)' 2>/dev/null)
FRONTEND_URL=$(gcloud run services describe tutor-frontend$SERVICE_SUFFIX --region $REGION --format 'value(status.url)' 2>/dev/null)

# Convert to WSS
MEDIAMIXER_WS_URL=$(echo $MEDIAMIXER_URL | sed 's/https/wss/')

echo ""
echo "🎉 Deployment Complete! ($ENV environment)"
echo ""
echo "📝 Service URLs:"
echo "  🌐 Frontend:     $FRONTEND_URL"
echo "  🔧 DASH API:     $DASH_URL"
echo "  🕵️  SherlockED:   $SHERLOCKED_URL"
echo "  📹 MediaMixer:   $MEDIAMIXER_URL"
echo ""
echo "🔗 WebSocket URLs:"
echo "  Command: ${MEDIAMIXER_WS_URL}/command"
echo "  Video:   ${MEDIAMIXER_WS_URL}/video"
echo ""

if [ "$ENV" = "staging" ]; then
    echo "💡 Note: If this is your first staging deployment, update this script with the actual URLs above"
    echo "    and redeploy to use correct frontend URLs."
fi