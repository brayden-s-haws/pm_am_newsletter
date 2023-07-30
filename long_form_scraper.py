import base64
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import re


# This is used to ensure we only get emails received in the last 24 hours
now = datetime.datetime.now()
twenty_four_hours_ago = now - datetime.timedelta(days=1)
timestamp = int(twenty_four_hours_ago.timestamp())


# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_credentials():
    """ Requests access to your Google project and stores credentials as a token. This prevents the need to re-authenticate each time.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'PATH TO YOUR GOOGLE API CREDENTIAL FILE', SCOPES)
            creds = flow.run_local_server(port=8080)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def scrape_gmail_articles():
    """ This scrapes the subject line and url for specified email based newsletters. These sites do not allow scraping so this is a workaround to get the content. These are all substack at the
    moment, but you can use this same approach to get content from other sources like Beehiiv
    :return: dict
    """
    import googleapiclient.discovery

    # Get credentials
    creds = get_credentials()

    # Call the Gmail API
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

    # Get today's date
    today = datetime.date.today().isoformat()

    # List of specific senders for which you want to grab data
    senders = ['COMMA SEPARATED LIST OF THE SENDERS YOU WISH TO SCRAPE DETAILS FROM']

    results = service.users().messages().list(userId='me', q=f'after:{timestamp}').execute()
    messages = results.get('messages', [])

    long_form_posts = {}
    counter = 1
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()

        # Extract email details
        headers = msg['payload']['headers']
        from_header = next((h for h in headers if h['name'] == 'From'), None)
        subject_header = next((h for h in headers if h['name'] == 'Subject'), None)

        if from_header and any(sender in from_header['value'] for sender in senders):
            subject = subject_header['value']
            # Decode email body
            if 'parts' in msg['payload']:
                part = msg['payload']['parts'][0]
                data = part['body']['data']
            else:
                data = msg['payload']['body']['data']

            byte_code = base64.urlsafe_b64decode(data.encode('ASCII'))
            content = byte_code.decode('utf-8')
            url_match = re.search(r'https?://[^\s]+', content)
            text = url_match.group(0) if url_match else 'No URL found'

            long_form_posts[counter] = {'subject': subject, 'url': text}
            counter += 1

    return long_form_posts

if __name__ == "__main__":
    long_form_posts = scrape_gmail_articles()

