1. Load the main Colection Page with parameters for file types (Praat and audio) (https://www.elararchive.org/index.php?name=SO_a863403a-0a7d-4c07-9252-dac4c6777054&hh_cmis_filter=imdi.mediaFileType/Audio|imdi.writtenFileType/Praat)

2. For pagination - iterate as long, as there is a "search-result" div.
3. For loop for pagination (```?pg=2```) added for pagination.
    0. Wait for the page to load.
    1. Get ```<div class="search-results">```
    2. Get the list of items -> ```<div id="post-****">``` and store it as a stack (or whatever)
    3. Loop to iterate through the stack
        1. Click on the item (or redirect to the link specified by onclick in the div)
        2. Wait for the page to load.
        3. Get ```<div class="search-results">```
        4. Within the div, get the list of Audio and Praat files
            - ```<div class="post-***">```, inside there has be ```<div class="archive_description col1">``` containing ```<p></p>``` or ```<p>wave</p>```
        5. Loop to iterate through the files
            1. Get the link from onclick of the "file" div
            2. Convert the link to the "download url", and download the file
                - ? is it possible to download somwhere else than the "Download" dir ?
