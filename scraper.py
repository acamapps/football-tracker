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
    """
    Extracts individual channel tags separately to add clean comma spacing,
    filtering out non-free/YouTube channels.
    """
    if not channel_div:
        return []
    
    # Extract text from individual sub-elements or split by standard tags
    raw_channels = [c.get_text(strip=True) for c in channel_div.find_all(['span', 'a', 'li'])]
    
    # Fallback if no sub-tags exist inside the channel div
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
        
    formatted_time = uk_time.strftime("%d %B %Y, %H:%M UK Time")
    
    output = f"# UK Free-To-Air Football Schedule\n"
    output += f"_Last updated: {formatted_time}_\n\n"
    
    # Locate main match grouping containers
    match_groups = soup.find_all(['div'], class_=['fixture__date', 'fixture'])
    
    total_matches_found = 0
    current_date_header = ""
    matches_in_current_date = 0

    for elem in match_groups:
        classes = elem.get('class', [])
        
        # When a Date Header is encountered
        if 'fixture__date' in classes:
            current_date_header = elem.get_text(strip=True)
            output += f"\n### 📅 {current_date_header}\n\n"
            matches_in_current_date = 0

        # When a Match Entry is encountered
        elif 'fixture' in classes:
            teams = elem.find("div", class_="fixture__teams")
            channel_div = elem.find("div", class_="fixture__channel")
            time = elem.find("div", class_="fixture__time")
            competition = elem.find("div", class_="fixture__competition")
            
            free_channels = parse_broadcasters(channel_div)
            
            if teams and free_channels:
                match_time = time.get_text(strip=True) if time else "TBD"
                team_text = teams.get_text(strip=True)
                comp_text = f" ({competition.get_text(strip=True)})" if competition else ""
                
                # Format channels into a clean comma-separated list
                channel_str = ", ".join(free_channels)
                
                output += f"- **{match_time}**: {team_text}{comp_text}\n  *Broadcaster(s): {channel_str}*\n\n"
                matches_in_current_date += 1
                total_matches_found += 1

    if total_matches_found == 0:
        output += "\nNo upcoming free-to-air UK matches listed at this time.\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(output)

if __name__ == "__main__":
    run_scraper()
