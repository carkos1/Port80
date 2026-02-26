import requests

def check_website(url):
    # The "I am a real person" disguise
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        return {
            "url": url,
            "status": response.status_code, # Should be 200
            "latency": round(response.elapsed.total_seconds(), 2)
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

# TEST ON A REALISTIC TARGET
print(check_website("https://www.cm-peniche.pt/"))