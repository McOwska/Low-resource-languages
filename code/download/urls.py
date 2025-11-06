def download_url(url):
    id = url.split('/')[-2]
    return f'https://www.elararchive.org/download/file/{id}'

def collection_url(page):
    return f'https://www.elararchive.org/?pg={page}&name=SO_a863403a-0a7d-4c07-9252-dac4c6777054&hh_cmis_filter=imdi.mediaFileType/Audio|imdi.writtenFileType/Praat'
