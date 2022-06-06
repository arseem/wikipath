# **WikiPath** 
**WikiPath** is a small web scraping project originating from an internet game of finding the shortest way to get from one Wikipedia article to another, clicking on the content section links only.<br>

## About the project
This simple script utilizes beautifulsoup library to parse html of the chosen Wikipedia article and extract all the links from the main content section. Then, performs the same action for pages under extracted links, creating directed tree of articles, until the destination page is found or maximum given range is exceeded.  

## Technologies in use
- Python
  - BeautifulSoup
  - requests
  - API
  - threading & concurrent.futures
## Requirements

<details>
  <summary>Click to expand</summary>
  <ul>
    beautifulsoup4==4.11.1<br>
    certifi==2022.5.18.1<br>
    charset-normalizer==2.0.12<br>
    idna==3.3<br>
    requests==2.27.1<br>
    soupsieve==2.3.2.post1<br>
    urllib3==1.26.9<br>
    Wikipedia-API==0.5.4<br>
  </ul>
</details>

## How to use
- Make sure you have Python and venv library installed and added to PATH
### Windows
- Run setup.ps1
### Other OS
- Create virtual environment in the base folder of an application and activate it using<br>
  > pip -m venv venv<br>
  > venv/Scripts/Activate.ps1<br>
- Make sure to have installed all of the depandancies from requirements.txt<br>
  > pip install -r requirements.txt
- Run main.py<br>
  > cd src<br>python main.py


### Alternatively (without virtual environment)
- Make sure to have installed all of the depandancies from requirements.txt<br>
  > pip install -r requirements.txt
- Run src/main.py (making sure that your base folder is /src)<br><br>

