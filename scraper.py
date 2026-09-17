import datetime
import requests
from bs4 import BeautifulSoup

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None

# Strict Allowlist: Only match genuine UK Free-to-Air TV and official free streams
UK_FREE_ALLOWLIST = [
    "bbc one", "bbc two", "bbc three", "bbc four", "bbc iplayer", "bbc red button", "bbc sport", "bbc scotland",
    "itv1", "itv4", "itvx", "itv",
    "channel 4", "channel 5", "5action", "quest",
    "s4c", "stv", "stv player", "freesports"
]

def parse_broadcasters(channel_div):
    if not channel_div:
        return []
    
    raw_channels = [c.get_text(strip=True) for c in channel_div.find_all(['span', 'a', 'li'])]
    if not raw_channels:
        raw_channels = [channel_div.get_text(strip=True)]
        
    free_found = []
    for ch in raw_channels:
        ch_lower = ch.lower()
        if "youtube" in ch_lower:
            continue
        if any(allowed in ch_lower for allowed in UK_FREE_ALLOWLIST):
            if ch not in free_found:
                free_found.append(ch)
                
    return free_found

def time_to_minutes(time_str):
    try:
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return -1

def run_scraper():
    url = "https://www.live-footballontv.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    if ZoneInfo:
        uk_time = datetime.datetime.now(ZoneInfo("Europe/London"))
    else:
        uk_time = datetime.datetime.now()
        
    formatted_date = uk_time.strftime("%A, %d %B %Y")
    formatted_timestamp = uk_time.strftime("%d %B %Y at %H:%M UK Time")
    
    output = f"# UK Free-To-Air Football ⚽\n"
    output += f"## 📅 Schedule for: {formatted_date}\n"
    output += f"_Last checked: {formatted_timestamp}_\n\n"
    
    match_groups = soup.find_all(['div'], class_=['fixture__date', 'fixture'])
    
    total_matches_found = 0
    previous_minutes = -1

    for elem in match_groups:
        classes = elem.get('class', [])
        
        # Stop collecting when date header changes or match times roll over
        if 'fixture' in classes:
            time_div = elem.find("div", class_="fixture__time")
            if not time_div:
                continue
                
            time_str = time_div.get_text(strip=True)
            current_minutes = time_to_minutes(time_str)
            
            if previous_minutes != -1 and current_minutes < previous_minutes:
                print(f"Time rollover detected ({time_str} after previous match). Stopping scrape.")
                break
            
            if current_minutes != -1:
                previous_minutes = current_minutes

            teams = elem.find("div", class_="fixture__teams")
            channel_div = elem.find("div", class_="fixture__channel")
            competition = elem.find("div", class_="fixture__competition")
            
            free_channels = parse_broadcasters(channel_div)
            
            if teams and free_channels:
                team_text = teams.get_text(strip=True)
                comp_text = f" ({competition.get_text(strip=True)})" if competition else ""
                channel_str = ", ".join(free_channels)
                
                output += f"- **{time_str}**: {team_text}{comp_text}\n  *Broadcaster(s): {channel_str}*\n\n"
                total_matches_found += 1

    if total_matches_found == 0:
        output += "No remaining free-to-air UK matches listed for today.\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    run_scraper()
