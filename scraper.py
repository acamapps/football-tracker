import datetime
import requests
from bs4 import BeautifulSoup

# Strictly UK Free-To-Air TV and Free Official Streaming channels
# Using exact matches to prevent accidental matches on global streaming platforms
STRICT_FREE_CHANNELS = [
    "BBC One", "BBC Two", "BBC Three", "BBC Four", "BBC iPlayer", "BBC Red Button", "BBC Sport Website",
    "ITV1", "ITV4", "ITVX", "ITV",
    "Channel 4", "S4C", "STV", "STV Player",
    "FreeSports", "Quest"
]

def is_strictly_free(channel_text):
    """
    Checks if a channel string contains a genuine UK free-to-air broadcast,
    while excluding generic or paid/international online services.
    """
    # Exclude common false positives like international hub channels
    exclusions = ["NWSL+", "AFC Hub", "DAZN", "TNT", "Sky", "Premier Sports"]
    for exc in exclusions:
        if exc.lower() in channel_text.lower():
            return False

    return any(free_ch.lower() in channel_text.lower() for free_ch in STRICT_FREE_CHANNELS)

def run_scraper():
    url = "https://www.live-footballontv.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    output = f"# UK Free-To-Air Football Schedule\n"
    output += f"_Last updated: {datetime.datetime.now().strftime('%d %B %Y, %H:%M UTC')}_\n\n"
    
    # Target all container elements (date headers and fixture blocks)
    elements = soup.find_all(['div'], class_=['fixture__date', 'fixture'])
    
    current_date = "Upcoming Matches"
    date_has_matches = False
    total_matches_found = 0

    for elem in elements:
        classes = elem.get('class', [])
        
        # When we encounter a Date Header
        if 'fixture__date' in classes:
            current_date = elem.get_text(strip=True)
            output += f"### 📅 {current_date}\n"
            date_has_matches = False

        # When we encounter a Match Block
        elif 'fixture' in classes:
            teams = elem.find("div", class_="fixture__teams")
            channel = elem.find("div", class_="fixture__channel")
            time = elem.find("div", class_="fixture__time")
            competition = elem.find("div", class_="fixture__competition")
            
            if teams and channel:
                channel_text = channel.get_text(strip=True)
                
                if is_strictly_free(channel_text):
                    match_time = time.get_text(strip=True) if time else "TBD"
                    team_text = teams.get_text(strip=True)
                    comp_text = f" ({competition.get_text(strip=True)})" if competition else ""
                    
                    output += f"- **{match_time}**: {team_text}{comp_text} — *{channel_text}*\n"
                    date_has_matches = True
                    total_matches_found += 1

    if total_matches_found == 0:
        output += "No upcoming free-to-air UK matches found listed on the page at this time.\n"

    # Write organized schedule back to README.md
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    run_scraper()
