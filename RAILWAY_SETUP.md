# Railway Environment Variables Setup

## Gmail OAuth 2.0 Configuration

To enable Gmail integration with OAuth 2.0, you need to set the following environment variables in your Railway project:

### Required Variables:

1. **GMAIL_OAUTH_CLIENT_ID**
   - Get this from: https://console.cloud.google.com/apis/credentials
   - Create OAuth 2.0 Client ID credentials
   - Application type: Web application
   - Authorized redirect URIs: `https://your-domain.railway.app/api/integrations/email/oauth/callback`

2. **GMAIL_OAUTH_CLIENT_SECRET**
   - Also from Google Cloud Console (same credentials page)
   - This is the client secret for your OAuth 2.0 client

3. **GMAIL_OAUTH_REDIRECT_URI**
   - Set to: `https://your-domain.railway.app/api/integrations/email/oauth/callback`
   - Replace `your-domain` with your actual Railway domain
   - This must match exactly what you set in Google Cloud Console

### Steps to Get Gmail OAuth Credentials:

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URI: `https://your-domain.railway.app/api/integrations/email/oauth/callback`
   - Copy the Client ID and Client Secret
5. Set in Railway:
   - Go to your Railway project
   - Click "Variables" tab
   - Add the three variables above with their values
   - Redeploy your service

### Important Notes:

- The redirect URI must use HTTPS (Railway provides this automatically)
- The redirect URI in Google Cloud Console must match exactly what you set in `GMAIL_OAUTH_REDIRECT_URI`
- After setting variables, you need to restart/redeploy your Railway service

