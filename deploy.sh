#!/bin/bash

# Configuration
PROJECT_ID="aitutor-473420"  # Change this!
REGION="us-central1"

echo "🚀 Deploying to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Submit build using cloudbuild.yaml
echo "📦 Starting Cloud Build..."
gcloud builds submit --config=cloudbuild.yaml .

# Get service URLs
echo ""
echo "🔍 Retrieving service URLs..."

DASH_URL=$(gcloud run services describe dash-api --region $REGION --format 'value(status.url)' 2>/dev/null)
SHERLOCKED_URL=$(gcloud run services describe sherlocked-api --region $REGION --format 'value(status.url)' 2>/dev/null)
MEDIAMIXER_URL=$(gcloud run services describe mediamixer --region $REGION --format 'value(status.url)' 2>/dev/null)
FRONTEND_URL=$(gcloud run services describe tutor-frontend --region $REGION --format 'value(status.url)' 2>/dev/null)

# Convert HTTPS to WSS for WebSocket
MEDIAMIXER_WS_URL=$(echo $MEDIAMIXER_URL | sed 's/https/wss/')

echo ""
echo "🎉 Deployment Complete!"
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
echo "⚠️  Update your frontend/.env.production with these URLs:"
echo ""
echo "VITE_DASH_API_URL=$DASH_URL"
echo "VITE_SHERLOCKED_API_URL=$SHERLOCKED_URL"
echo "VITE_MEDIAMIXER_COMMAND_WS=${MEDIAMIXER_WS_URL}/command"
echo "VITE_MEDIAMIXER_VIDEO_WS=${MEDIAMIXER_WS_URL}/video"
echo ""