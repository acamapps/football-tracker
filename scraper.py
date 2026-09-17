import datetime
import requests
from bs4 import BeautifulSoup

# Strict Allowlist: Only match genuine UK Free-to-Air TV and official free streams
UK_FREE_ALLOWLIST = [
    "bbc one", "bbc two", "bbc three", "bbc four", "bbc iplayer", "bbc red button", "bbc sport",
    "itv1", "itv4", "itvx", "itv",
    "channel 4", "channel 5", "5action", "quest",
    "s4c", "stv", "stv player", "freesports"
]

def is_uk_free_to_air(channel_text):
    """
    Returns True ONLY if the broadcast string contains a known UK free-to-air provider.
    Any unknown streaming hub, pay-TV channel, or foreign stream is ignored automatically.
    """
    text_lower = channel_text.lower()
    return any(allowed in text_lower for allowed in UK_FREE_ALLOWLIST)

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
    
    elements = soup.find_all(['div'], class_=['fixture__date', 'fixture'])
    
    total_matches_found = 0

    for elem in elements:
        classes = elem.get('class', [])
        
        # Capture Date Headers
        if 'fixture__date' in classes:
            current_date = elem.get_text(strip=True)
            output += f"\n### 📅 {current_date}\n"

        # Capture Match Block
        elif 'fixture' in classes:
            teams = elem.find("div", class_="fixture__teams")
            channel = elem.find("div", class_="fixture__channel")
            time = elem.find("div", class_="fixture__time")
            competition = elem.find("div", class_="fixture__competition")
            
            if teams and channel:
                channel_text = channel.get_text(strip=True)
                
                # Check against strictly defined UK Free Allowlist
                if is_uk_free_to_air(channel_text):
                    match_time = time.get_text(strip=True) if time else "TBD"
                    team_text = teams.get_text(strip=True)
                    comp_text = f" ({competition.get_text(strip=True)})" if competition else ""
                    
                    output += f"- **{match_time}**: {team_text}{comp_text} — *{channel_text}*\n"
                    total_matches_found += 1

    if total_matches_found == 0:
        output += "\nNo upcoming free-to-air UK matches listed at this time.\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    run_scraper()
