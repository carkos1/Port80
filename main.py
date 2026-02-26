import requests
import csv
from bs4 import BeautifulSoup
import time
from urllib.parse import quote, urljoin
import urllib3

URL_BASE = "https://www.diretorio-exemplo.com/searches"
URL_CRAWL = "https://www.diretorio-exemplo.com/"
URL_MODE = "restaurantes/"
REGIOES = ["Alenquer","Amadora","Arruda dos Vinhos","Azambuja","Cadaval","Cascais","Lisboa","Loures","Lourinha","Mafra","Odivelas","Oeiras","Sintra","Sobral de Monte Agraco","Torres Vedras","Vila Franca de Xira"]
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3','Accept-Language':'en-US'}

def urlcrawer_engine():
    dic = []
    seen_urls = set()
    url_round = []
    for region in REGIOES:
        print("Starting crawl for region " + region)

        payload = {
            "search[query]": "restaurantes",  
            "search[location]": region,       
            "search[location_value]": region, 
            "commit": "Procurar"              
        }
        u = URL_CRAWL + URL_MODE + region.lower().replace(" ","-")
        try:
            r = requests.get(u, headers=headers)
            r.raise_for_status()
        except Exception as e:
            print(f"Could not load first page in region {region}: {e}")
            continue
        
        page_count = 1
        while True:
            try:
                old_round = url_round
                url_round = []
                print(f"Processing Page {page_count}...")
                soup = BeautifulSoup(r.text, features="lxml")
                if soup == None:
                    break
                new_leads = gethref(soup)
                for lead in new_leads:
                    url_round.append(lead['Url'])
                    if lead['Url'] not in seen_urls:
                        dic.append(lead)          
                        seen_urls.add(lead['Url'])
                nextpage = soup.find("li", class_= "next")
                if nextpage == None:
                    print("No 'Next' button found. Crawl finished.")
                    break
                
                nextpage_link = nextpage.find("a")
                if nextpage_link == None:
                    break
                
                url = urljoin(URL_CRAWL,nextpage_link["href"])

                time.sleep(2)
                try:
                    r = requests.get(url,headers=headers)
                    if old_round == url_round:
                        break
                except Exception as e:
                    print(f"Request after {e}...")
                    time.sleep(5)
                    try:
                        r = requests.get(url,headers=headers)
                    except:
                        break

                page_count += 1
            except Exception as e:
                print(f"CRITICAL ERROR: {e}")
                break
    save_to_excel(dic)

def gethref(soup):
    dic = []
    store = soup.find_all("a", class_="card-link")
    if store:
            for i in store:
                a = i["href"]
                time.sleep(2)
                url = store_url(a)  
                if url != None:         
                    dic.append(url)
                
    return dic


def store_url(href):
    url = urljoin(URL_CRAWL,href)
    try:
        r = requests.get(url,headers=headers)
        r.raise_for_status()
    except Exception as e:
                print(f"Request after {e}...")
                time.sleep(5)
                try:
                    r = requests.get(url,headers=headers)
                except:
                    return None

    soup = BeautifulSoup(r.text, features="lxml")
    try:
        btn_phone = soup.find("button", attrs={"data-trackable-event": "call-phone"})
        name_tag = soup.find("h2", class_ = "desktop-title")
        name = name_tag.get_text(strip=True) if name_tag else "Unknown"
        email = "Not Listed"
    
        try:
            lists = soup.find_all("li", class_="listing-item")
            
            for l in lists:
                a_tag = l.find("a")
                if a_tag and a_tag.has_attr("href"):
                    href_str = str(a_tag["href"])
                    if href_str.startswith("mailto:"):
                        email_raw = href_str.split(":")[1]
                        email = email_raw.split("?")[0].strip()
                        break
            
                        
        except Exception as e:
            print(f"Erro a processar e-mail: {e}")

        if btn_phone:
            phone = btn_phone.get("value")
        else:
            phone = "Not Listed"
    except:
        phone = None
    try:
        website = soup.find_all("li", class_ = "listing-item")
        for i in website:
            try:
                a = i.find("a")
                if( a and str(a["href"]).startswith("http")):
                    url_store = a["href"]
                    return getstatus(str(url_store),phone,name, email)
            except:
                continue
        if phone:
            return {
                "Name": name,
                "Email":email,
                "Url": "NO WEBSITE", 
                "Phone": str(phone), 
                "Security": "NULL", 
                "Status": "NO WEBSITE", 
                "Latency": "NULL"
            }
    except Exception as e:
        print(f"Error getting store website! {e}")
    

def getstatus(url:str, phone, name, email):
    
    try:
        r = requests.get(url, headers=headers, timeout=5, verify=False)
        dic = {
            "name":name,
            "email":email,
            "url":r.url,
            "phone":phone,
            "status":r.status_code,
            "latency":round(r.elapsed.total_seconds(), 2)
        }
        return test_request(dic, url, phone, name,email)
    except requests.exceptions.Timeout:
        return {"Name": name,"Email":email,"Url": url, "Phone": phone, "Security": "False", "Status": "TIMEOUT", "Latency": ">5s"}
        
    except requests.exceptions.SSLError:
        return {"Name": name,"Email":email,"Url": url, "Phone": phone, "Security": "False", "Status": "SSL_ERROR", "Latency": "999"}
        
    except requests.exceptions.ConnectionError:
        return {"Name": name,"Email":email,"Url": url, "Phone": phone, "Security": "False", "Status": "CONNECTION_REFUSED", "Latency": "999"}
        
    except Exception as e:
        if "facebook" in url or "instagram" in url:
            return{"Name": name,"Email":email,"Url": url, "Phone": phone, "Security": "Social Page", "Status": "Social Page", "Latency": "Social Page"}
        return {"Name": name,"Email":email,"Url": url, "Phone": phone, "Security": "False", "Status": f"ERROR_{str(e)[:20]}", "Latency": "999"}

def test_request(request:dict, url:str, phone, name,email):
    dic = {"Name":"","Email":"","Url":"","Security":"","Status":"", "Latency":""}
    sec = False 
    speed = False
    con = False
    if not request:
        print("request is empty")
        return
    status_code = request["status"]
    if request["url"].startswith("https"):
        sec = True
    if request["status"] == 200:
        con = True
        
    speed = request["latency"]
        
    if (sec == True and con == True and speed < 3) and not ("facebook" in url or "instagram" in url):
        return None
    dic.update({"Name": name,"Email":email,"Url":url,"Phone":str(phone),"Security":str(sec),"Status":str(status_code),"Latency":str(speed)})
    return dic

def save_to_excel(dic):
    audit_list = []
    social_list = []
    blacklist = ['tripadvisor', 'thefork', 'zomato', 'yelp', 'pai.pt', 'eatbu', 'wix', 'google']

    for row in dic:
        url = row['Url'].lower()
        if any(bad_word in url for bad_word in blacklist):
            continue
        if 'facebook' in url or 'instagram' in url:
            social_list.append(row)
        else:
            audit_list.append(row)
            
    with open("Stores_Websites.csv", mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, ["Name","Email","Url","Phone","Security","Status","Latency"])
        writer.writeheader()
        writer.writerows(audit_list)
        
    with open("Stores_Social.csv", mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, ["Name","Email","Url","Phone","Security","Status","Latency"])
        writer.writeheader()
        writer.writerows(social_list)
        
    print(f"Saved {len(audit_list)} Website Leads.")
    print(f"Saved {len(social_list)} Social Media Leads.")
def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    urlcrawer_engine()

if __name__ == "__main__":
        main()