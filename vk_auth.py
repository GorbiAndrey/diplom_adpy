from urllib.parse import urlencode


APP_VK_ID = 7561411
AUTH_URL = 'https://oauth.vk.com/authorize'
AUTH_DATA = {
    'client_id': APP_VK_ID,
    'redirect_uri': 'https://oauth.vk.com/blank.html',
    'display': 'page',
    'scope': 'friends,groups',
    'response_type': 'token',
}
print('?'.join((AUTH_URL, urlencode(AUTH_DATA))))
