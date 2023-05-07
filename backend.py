import requests
import re

uk_base_url = "https://www.macmillandictionary.com/dictionary/british/"
us_base_url = "https://www.macmillandictionary.com/us/dictionary/american/"

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'
}

def download(word, filepath, accent):
    url = build_url(accent, word)
    response = make_request(url)

    if response[0] == 200: 
        body = response[1].text

        if word_found(body): 
            audio_url = re.findall("https.*?mp3", body)[0]            
            audio_response = make_request(audio_url)

            if audio_response[0] == 200:
                open(filepath, "wb").write(audio_response[1].content)
                return 200, "success"
            
            else: 
                return response[0], response[1]
        else:
            return "Not found", "Word not found."
    
    elif response[0] != 200:
        return response[0], response[1]

def build_url(accent, word):
    return uk_base_url + word if accent == "uk_accent" else us_base_url + word

def word_found(body):
    found_word = re.findall("Sorry, no search result", body)
    return True if "Sorry, no search result" not in found_word else False

def make_request(url):
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.status_code, response

    except requests.exceptions.HTTPError as errh:
        return "ERROR", "HTTP Error"

    except requests.exceptions.ConnectionError as errc:
        return "ERROR", "Connection Error"
    
    except requests.exceptions.Timeout as errt:
        return "ERROR", "Timeout Error"
    
    except requests.exceptions.RequestException as err:
        return "ERROR", "OOps: Something Else"
