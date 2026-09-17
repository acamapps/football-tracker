import datetime
import requests
from bs4 import BeautifulSoup

# Define Free-To-Air / Free-Streaming channels in the UK
FREE_CHANNELS = [
    "BBC", "BBC One", "BBC Two", "BBC Three", "BBC Four", "BBC iPlayer", "BBC Red Button",
    "ITV", "ITV1", "ITV4", "ITVX", "Channel 4", "S4C", "STV", "STV Player", "YouTube", "FreeSports"
]

def run_scraper():
    url = "https://www.live-footballontv.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to reach website.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    match_blocks = soup.find_all("div", class_="fixture")
    
    free_matches = []

    for match in match_blocks:
        # Extract fixture details safely
        teams = match.find("div", class_="fixture__teams")
        channel = match.find("div", class_="fixture__channel")
        time = match.find("div", class_="fixture__time")
        
        if teams and channel:
            channel_text = channel.get_text(strip=True)
            # Check if match is broadcast on a free channel
            if any(free in channel_text for free in FREE_CHANNELS):
                match_time = time.get_text(strip=True) if time else "TBD"
                free_matches.append(f"- **{match_time}**: {teams.get_text(strip=True)} (*{channel_text}*)")

    # Format output content
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    output = f"# Free Football Matches UK - {today_date}\n\n"
    
    if free_matches:
        output += "\n".join(free_matches)
    else:
        output += "No free-to-air matches listed for today."

    # Save output directly to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    run_scraper()
