from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from .models import GoogleCredentials


def get_oauth2_flow(request):
    return InstalledAppFlow.from_client_secrets_file(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_FILE,
        scopes=settings.GOOGLE_OAUTH2_SCOPES,
        redirect_uri=request.build_absolute_uri(
            reverse('google_auth_callback'))
    )


def google_authenticate(request):
    flow = get_oauth2_flow(request)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['oauth2_state'] = state
    return redirect(authorization_url)


def google_oauth2_callback(request):
    state = request.session.pop('oauth2_state', None)
    if state is None or state != request.GET.get('state'):
        return redirect(reverse('admin:login'))  # Handle error, invalid state

    flow = get_oauth2_flow(request)
    flow.fetch_token(code=request.GET.get('code'))

    credentials = flow.credentials

    # Save credentials to database (assuming user is logged in)
    user_credentials, created = GoogleCredentials.objects.get_or_create()
    user_credentials.credentials = credentials.to_json()
    user_credentials.save()

    # Redirect to admin index or wherever needed
    return redirect(reverse('admin:index'))
