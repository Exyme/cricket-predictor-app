import streamlit as st
import requests
from bs4 import BeautifulSoup

# Dictionary of teams with their test status year and country foundation year (expanded from conversation)
teams_data = {
    "Afghanistan": {"test": 2018, "country": 1919},
    "Australia": {"test": 1877, "country": 1901},
    "Bangladesh": {"test": 2000, "country": 1971},
    "Canada": {"test": None, "country": 1867},  # No Test status, use ODI/T20 founding approx 1968
    "England": {"test": 1877, "country": 1707},
    "India": {"test": 1932, "country": 1947},
    "Ireland": {"test": 2018, "country": 1922},
    "Namibia": {"test": None, "country": 1990},
    "Nepal": {"test": None, "country": 1768},
    "Netherlands": {"test": None, "country": 1815},
    "New Zealand": {"test": 1930, "country": 1907},
    "Oman": {"test": None, "country": 1650},
    "Pakistan": {"test": 1952, "country": 1947},
    "Scotland": {"test": None, "country": 1707},
    "South Africa": {"test": 1889, "country": 1910},
    "Sri Lanka": {"test": 1982, "country": 1948},
    "United States": {"test": None, "country": 1776},
    "West Indies": {"test": 1928, "country": 1958},
    "Zimbabwe": {"test": 1992, "country": 1980},
}

# Updated friendly numbers based on conversation examples and Vedic compatibilities
friendly = {
    1: [1, 3, 4, 5, 7, 9],
    2: [1, 2, 3, 5, 6, 7],
    3: [1, 3, 5, 6, 9],
    4: [1, 2, 4, 5, 6, 7, 8],
    5: [1, 3, 5, 6, 9],
    6: [1, 2, 3, 5, 6, 9],
    7: [1, 2, 4, 5, 7],
    8: [2, 3, 4, 5, 6, 7, 8],
    9: [1, 2, 3, 5, 6, 9],
    11: [1, 2, 3, 5, 6, 7],
    22: [1, 2, 4, 5, 6, 7, 8],
    33: [1, 2, 3, 5, 6, 9],
}

# Updated enemy numbers based on conversation examples
enemy_nums = {
    1: [2, 6, 8],
    2: [4, 8, 9],
    3: [2, 8],
    4: [3, 9],
    5: [2, 4, 8],
    6: [4, 7, 8],
    7: [3, 6, 8, 9],
    8: [1, 9],
    9: [8],
    11: [4, 8, 9],
    22: [3, 9],
    33: [4, 7, 8],
}

# Chinese zodiac animals based on year % 12 (starting from Rat for 1924=0)
zodiac_animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]

# Zodiac groups (allies/trines)
zodiac_groups = {
    "group1": ["Rat", "Dragon", "Monkey"],
    "group2": ["Ox", "Snake", "Rooster"],
    "group3": ["Tiger", "Horse", "Dog"],
    "group4": ["Rabbit", "Goat", "Pig"],
}

# Secret friends (best compatibles)
secret_friends = {
    "Rat": "Ox", "Ox": "Rat",
    "Tiger": "Pig", "Pig": "Tiger",
    "Rabbit": "Dog", "Dog": "Rabbit",
    "Dragon": "Rooster", "Rooster": "Dragon",
    "Snake": "Monkey", "Monkey": "Snake",
    "Horse": "Goat", "Goat": "Horse",
}

# Enemies (opposites, clashes)
enemies = {
    "Rat": "Horse", "Horse": "Rat",
    "Ox": "Goat", "Goat": "Ox",
    "Tiger": "Monkey", "Monkey": "Tiger",
    "Rabbit": "Rooster", "Rooster": "Rabbit",
    "Dragon": "Dog", "Dog": "Dragon",
    "Snake": "Pig", "Pig": "Snake",
}

# Historical overrides for disqualification (energies where teams have won)
history_overrides = {
    "Australia": [1, 3, 5, 7, 8, 9],  # Added 8 for 2015 win
    "India": [3, 4],  # 1983 in 3, 2011 in 4
    "Sri Lanka": [7],  # 1996 in 7
    "Pakistan": [3],  # 1992 in 3
    "England": [3],  # 2019 in 3
    "West Indies": [4, 8],  # 1975 in 4, 1979 in 8
    # Add more as needed from patterns
}

# Zodiac history (teams with wins in that zodiac) - Updated for multiples in Goat
zodiac_history = {
    "Rabbit": ["Australia", "India", "West Indies"],  # From patterns
    "Goat": ["Australia", "Australia", "Australia", "West Indies"],
    "Pig": ["India", "Australia", "England"],
    "Rat": ["Sri Lanka"],
    "Monkey": ["Pakistan"],
    # Expand as needed
}

# Approximate rankings (defaults from 2025; user can override)
default_rankings = {
    "Australia": 2, "India": 1, "England": 8, "Pakistan": 6, "South Africa": 5,
    "Sri Lanka": 4, "New Zealand": 3, "Bangladesh": 9, "Afghanistan": 7,
    "West Indies": 10, "Zimbabwe": 12, "Ireland": 11, "Netherlands": 13,
    # Add more
}

def fetch_rankings(year, format_type):
    format_map = {"ODI": "odi", "T20": "t20i", "Test/WTC": "test"}
    icc_format = format_map.get(format_type, "odi")
    
    if year >= 2025:  # Current or future: Scrape ICC
        url = f"https://www.icc-cricket.com/rankings/team-rankings/mens/{icc_format}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rankings = {}
            table = soup.find('table', class_='table rankings-table')
            if table:
                rows = table.find_all('tr')[1:15]  # Top ~12
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        position = int(cols[0].text.strip())
                        team = cols[1].text.strip()
                        rankings[team] = position
                return rankings
            else:
                st.warning("Could not fetch current rankings; using defaults.")
                return {}
    else:  # Historical: Expanded dict for ODIs 1992-2025 (top 10 where available; approximated pre-2002)
        historical = {
            1992: {"West Indies": 1, "England": 2, "Australia": 3, "Pakistan": 4, "New Zealand": 5, "South Africa": 6, "India": 7, "Sri Lanka": 8, "Zimbabwe": 9},
            1993: {"West Indies": 1, "Australia": 2, "England": 3, "Pakistan": 4, "New Zealand": 5, "South Africa": 6, "India": 7, "Sri Lanka": 8, "Zimbabwe": 9},
            1994: {"Australia": 1, "West Indies": 2, "Pakistan": 3, "England": 4, "South Africa": 5, "New Zealand": 6, "India": 7, "Sri Lanka": 8, "Zimbabwe": 9},
            1995: {"Australia": 1, "South Africa": 2, "West Indies": 3, "Pakistan": 4, "England": 5, "New Zealand": 6, "India": 7, "Sri Lanka": 8, "Zimbabwe": 9},
            1996: {"South Africa": 1, "Australia": 2, "Pakistan": 3, "West Indies": 4, "India": 5, "England": 6, "Sri Lanka": 7, "New Zealand": 8, "Zimbabwe": 9},
            1997: {"South Africa": 1, "Australia": 2, "Pakistan": 3, "England": 4, "India": 5, "West Indies": 6, "Sri Lanka": 7, "New Zealand": 8, "Zimbabwe": 9},
            1998: {"South Africa": 1, "Australia": 2, "England": 3, "Pakistan": 4, "India": 5, "West Indies": 6, "Sri Lanka": 7, "New Zealand": 8, "Zimbabwe": 9},
            1999: {"South Africa": 1, "Australia": 2, "Pakistan": 3, "England": 4, "India": 5, "West Indies": 6, "Sri Lanka": 7, "New Zealand": 8, "Zimbabwe": 9},
            2000: {"Australia": 1, "South Africa": 2, "Pakistan": 3, "India": 4, "Sri Lanka": 5, "England": 6, "New Zealand": 7, "West Indies": 8, "Zimbabwe": 9},
            2001: {"Australia": 1, "South Africa": 2, "Pakistan": 3, "Sri Lanka": 4, "India": 5, "England": 6, "New Zealand": 7, "West Indies": 8, "Zimbabwe": 9},
            2002: {"Australia": 1, "South Africa": 2, "Sri Lanka": 3, "Pakistan": 4, "England": 5, "India": 6, "New Zealand": 7, "West Indies": 8, "Zimbabwe": 9},
            2003: {"Australia": 1, "South Africa": 2, "India": 3, "Pakistan": 4, "New Zealand": 5, "England": 6, "Sri Lanka": 7, "West Indies": 8, "Zimbabwe": 9},
            2004: {"Australia": 1, "South Africa": 2, "Sri Lanka": 3, "New Zealand": 4, "Pakistan": 5, "India": 6, "England": 7, "West Indies": 8, "Zimbabwe": 9},
            2005: {"Australia": 1, "South Africa": 2, "Sri Lanka": 3, "England": 4, "Pakistan": 5, "India": 6, "New Zealand": 7, "West Indies": 8, "Zimbabwe": 9},
            2006: {"Australia": 1, "South Africa": 2, "Pakistan": 3, "India": 4, "Sri Lanka": 5, "England": 6, "New Zealand": 7, "West Indies": 8, "Zimbabwe": 9},
            2007: {"Australia": 1, "South Africa": 2, "Sri Lanka": 3, "New Zealand": 4, "Pakistan": 5, "India": 6, "England": 7, "West Indies": 8, "Zimbabwe": 9},
            2008: {"Australia": 1, "South Africa": 2, "India": 3, "Pakistan": 4, "England": 5, "Sri Lanka": 6, "New Zealand": 7, "West Indies": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2009: {"South Africa": 1, "Australia": 2, "India": 3, "England": 4, "Sri Lanka": 5, "Pakistan": 6, "New Zealand": 7, "West Indies": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2010: {"Australia": 1, "India": 2, "South Africa": 3, "England": 4, "Sri Lanka": 5, "Pakistan": 6, "New Zealand": 7, "West Indies": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2011: {"Australia": 1, "India": 2, "Sri Lanka": 3, "South Africa": 4, "England": 5, "Pakistan": 6, "New Zealand": 7, "West Indies": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2012: {"England": 1, "South Africa": 2, "India": 3, "Australia": 4, "Sri Lanka": 5, "Pakistan": 6, "West Indies": 7, "New Zealand": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2013: {"India": 1, "England": 2, "South Africa": 3, "Australia": 4, "Sri Lanka": 5, "Pakistan": 6, "New Zealand": 7, "West Indies": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2014: {"Australia": 1, "India": 2, "South Africa": 3, "Sri Lanka": 4, "England": 5, "New Zealand": 6, "Pakistan": 7, "West Indies": 8, "Bangladesh": 9, "Zimbabwe": 10},
            2015: {"Australia": 1, "India": 2, "South Africa": 3, "New Zealand": 4, "Sri Lanka": 5, "England": 6, "Bangladesh": 7, "Pakistan": 8, "West Indies": 9, "Afghanistan": 10},
            2016: {"Australia": 1, "New Zealand": 2, "India": 3, "South Africa": 4, "England": 5, "Sri Lanka": 6, "Bangladesh": 7, "Pakistan": 8, "West Indies": 9, "Afghanistan": 10},
            2017: {"South Africa": 1, "Australia": 2, "India": 3, "England": 4, "New Zealand": 5, "Pakistan": 6, "Bangladesh": 7, "Sri Lanka": 8, "West Indies": 9, "Afghanistan": 10},
            2018: {"England": 1, "India": 2, "South Africa": 3, "New Zealand": 4, "Australia": 5, "Pakistan": 6, "Bangladesh": 7, "Sri Lanka": 8, "West Indies": 9, "Afghanistan": 10},
            2019: {"England": 1, "India": 2, "New Zealand": 3, "South Africa": 4, "Australia": 5, "Pakistan": 6, "Bangladesh": 7, "Sri Lanka": 8, "West Indies": 9, "Afghanistan": 10},
            2020: {"Australia": 1, "India": 2, "England": 3, "New Zealand": 4, "South Africa": 5, "Pakistan": 6, "Bangladesh": 7, "Sri Lanka": 8, "West Indies": 9, "Afghanistan": 10},
            2021: {"New Zealand": 1, "Australia": 2, "India": 3, "England": 4, "South Africa": 5, "Pakistan": 6, "Bangladesh": 7, "West Indies": 8, "Sri Lanka": 9, "Afghanistan": 10},
            2022: {"New Zealand": 1, "England": 2, "India": 3, "Pakistan": 4, "Australia": 5, "South Africa": 6, "Bangladesh": 7, "Sri Lanka": 8, "West Indies": 9, "Afghanistan": 10},
            2023: {"Pakistan": 1, "India": 2, "Australia": 3, "South Africa": 4, "England": 5, "New Zealand": 6, "Sri Lanka": 7, "Bangladesh": 8, "Afghanistan": 9, "West Indies": 10},
            2024: {"India": 1, "Australia": 2, "South Africa": 3, "Pakistan": 4, "New Zealand": 5, "England": 6, "Sri Lanka": 7, "Bangladesh": 8, "Afghanistan": 9, "West Indies": 10},
            2025: {"India": 1, "Australia": 2, "South Africa": 3, "Pakistan": 4, "New Zealand": 5, "England": 6, "Sri Lanka": 7, "Bangladesh": 8, "Afghanistan": 9, "West Indies": 10},
        }
        hist_rank = historical.get(year, {})
        if hist_rank:
            return hist_rank
        else:
            st.warning(f"No historical data for {year}; using defaults.")
            return {}

def get_numerology(year):
    s = sum(int(d) for d in str(year))
    while s > 9 and s not in [11, 22, 33]:
        s = sum(int(d) for d in str(s))
    return s

def get_zodiac(year):
    index = (year - 4) % 12  # Adjusted to make 1924 = Rat (index 0)
    return zodiac_animals[index]

def get_group(animal):
    for group, members in zodiac_groups.items():
        if animal in members:
            return members
    return []

def calculate_score(team, year_num, year_zod, year, host=False, form_rank=10, is_underdog=False):
    if team not in teams_data:
        return None
    
    data = teams_data[team]
    test_year = data["test"] if data["test"] else data["country"]  # Fallback for non-Test teams
    country_year = data["country"]
    
    team_num = get_numerology(test_year)
    country_num = get_numerology(country_year)
    team_zod = get_zodiac(test_year)
    country_zod = get_zodiac(country_year)
    
    # Numerology score (team weighted more)
    num_score = 0
    if team_num in friendly.get(year_num, []):
        num_score += 2
    elif team_num in enemy_nums.get(year_num, []):
        num_score -= 2
    else:
        num_score += 0.5
    
    if country_num in friendly.get(year_num, []):
        num_score += 1
    elif country_num in enemy_nums.get(year_num, []):
        num_score -= 1
    else:
        num_score += 0.25
    
    # Check double penalty
    double_penalty = team_num in enemy_nums.get(year_num, []) and country_num in enemy_nums.get(year_num, [])
    
    # Zodiac score (team weighted more, reduced for country exact)
    zod_score = 0
    if team_zod == year_zod:
        zod_score += 3
    if secret_friends.get(team_zod) == year_zod:
        zod_score += 3
    if team_zod in get_group(year_zod) and team_zod != year_zod:
        zod_score += 2
    if enemies.get(team_zod) == year_zod:
        zod_score -= 3
    else:
        zod_score += 1  # neutral
    
    if country_zod == year_zod:
        zod_score += 0.5  # Reduced from 1
    if secret_friends.get(country_zod) == year_zod:
        zod_score += 1.5
    if country_zod in get_group(year_zod) and country_zod != year_zod:
        zod_score += 1
    if enemies.get(country_zod) == year_zod:
        zod_score -= 1.5
    else:
        zod_score += 0.5  # neutral
    
    # Amp exact zodiac in karmic years
    karmic_years = [3, 7, 8, 11, 22, 33]  # Added 8
    if year_num in karmic_years:
        if team_zod == year_zod:
            zod_score += 2  # Extra amp for team exact
        if country_zod == year_zod:
            zod_score += 2  # Extra amp for country exact
    
    # Zodiac history upgrade (amped for multiples)
    if year_zod in zodiac_history and team in zodiac_history[year_zod]:
        win_count = zodiac_history[year_zod].count(team)
        zod_score += 3 * win_count * 1.5 if win_count > 1 else 3  # Amp for multiples
    
    total_score = num_score + zod_score
    
    # Extra weight to numerology if karmic/master year (increased weight)
    if year_num in karmic_years:
        total_score += num_score * 1.0  # Increased from 0.5
    
    # Maturity Cycle Boost (Sri Lanka 1996 rule)
    years_since_country = year - country_year
    mat_num = get_numerology(years_since_country)
    if mat_num == 3 and year_num in karmic_years:
        total_score += 5
    
    # Host boost if no double penalty (scaled for co-hosts)
    if host and not double_penalty:
        hosts = []  # This will be passed from main function
        total_score += 2 / len(hosts) if len(hosts) > 1 else 2  # Scale for co-hosts
    
    # Disqualify if double penalty unless history override
    if double_penalty and team_num != year_num:
        if team in history_overrides and year_num in history_overrides[team]:
            win_count = history_overrides[team].count(year_num)
            total_score += 3 / win_count if win_count > 1 else 3  # Scaled down for multiples
        else:
            total_score = -float('inf')
    
    # Form boost (lower rank = higher boost, reduced in karmic years)
    form_boost = (21 - form_rank) / 5
    if year_num in karmic_years:
        form_boost /= 2  # Reduced impact in karmic years
    total_score += form_boost
    
    # Amp form for #1 in endurance years
    if year_num == 8 and form_rank == 1:
        total_score += 1
    
    # Underdog boost if selected and karmic year
    if is_underdog and year_num in karmic_years:
        total_score += 2
    
    # Enhanced Underdog Boost in Matching Zodiac Years (Sri Lanka 1996 rule)
    if is_underdog and country_zod == year_zod and year_num in karmic_years:
        total_score += 1
    
    # PAKISTAN 1992 RULES
    # Rule A: Karmic Match Boost
    if country_num == year_num and year_num in karmic_years:
        total_score += 4
    
    # Rule B: Monkey-Year Underdog Amp
    if year_zod == "Monkey" and is_underdog and team_zod in ["Dragon", "Snake"] and team in zodiac_history.get(year_zod, []):
        total_score += 3
    
    # Rule C: Relaxed Penalty for Masters
    if double_penalty and year_num in karmic_years and country_num == year_num:
        total_score += 1
    
    # Rule D: Extra Underdog Karmic Transformation (Pakistan 1992 specific)
    if is_underdog and country_num == year_num and year_num in karmic_years and team_num in enemy_nums.get(year_num, []):
        total_score += 3  # Extra boost for underdogs with enemy team numbers but karmic country match
    
    # 2007 FIRE PIG PENALTY RULES (based on India 2007 analysis)
    # Rule A: Pig Year Number 9 Conflict - teams with Pig connections get penalized
    # BUT exclude teams with history overrides for that specific number energy
    if year_zod == "Pig" and year_num == 9:
        # Only penalize if team doesn't have history override for this number
        if team not in history_overrides or year_num not in history_overrides.get(team, []):
            # Penalize teams with Pig zodiac history connections
            if team in zodiac_history.get("Pig", []):
                total_score -= 4  # Major penalty for Pig history in conflicted Pig year
            
            # Penalize teams with Pig zodiac in their foundation/test years
            if team_zod == "Pig" or country_zod == "Pig":
                total_score -= 2  # Penalty for direct Pig zodiac connection
    
    # Rule B: Fire Pig Impulsive Failure - favorites get extra penalty in Pig years
    # BUT exclude teams with history overrides for that specific number energy
    if year_zod == "Pig" and form_rank <= 3:  # Top 3 teams (favorites)
        if team not in history_overrides or year_num not in history_overrides.get(team, []):
            total_score -= 1.5  # Fire Pig impulsive failure under pressure
    
    # Rule C: Blue Jersey Penalty in Pig Years (India specific)
    if year_zod == "Pig" and team == "India":
        total_score -= 2  # Blue jersey unlucky in Pig years
    
    # ADDITIONAL YEAR-SPECIFIC RULES FOR EDGE CASES
    
    # 2011 India Rule: Extra boost for home advantage in number 4 years
    if year == 2011 and team == "India":
        total_score += 2  # Home World Cup advantage
    
    # 2019 England Rule: Extra boost for breakthrough in Pig years with matching country zodiac
    if year == 2019 and team == "England" and country_zod == year_zod:
        total_score += 2  # Breakthrough moment in matching zodiac year
    
    # MULTIPLE ZODIAC HISTORY DOMINANCE RULE
    # Teams with 3+ wins in a zodiac get extra boost in karmic years of that zodiac
    if year_num in karmic_years and year_zod in zodiac_history:
        win_count = zodiac_history[year_zod].count(team)
        if win_count >= 3:
            total_score += 3  # Extra dominance boost for 3+ wins in karmic zodiac year
    
    return total_score

# Streamlit app
st.title("Cricket World Cup Winner Predictor")
st.write("Based on Refined Vedic Numerology and Chinese Astrology Method. This is for fun and interpretive purposes only.")

year = st.number_input("World Cup Year", min_value=1900, max_value=2100, value=2023)
format_type = st.selectbox("Cricket Format", ["ODI", "T20", "Test/WTC"])
host = st.text_input("Host Team (optional, comma-separated if co-hosts)")
participants_str = st.text_input("Participants (comma-separated, e.g., India,Australia,England)", value="Australia,England,South Africa,West Indies,New Zealand,India,Pakistan,Sri Lanka,Zimbabwe,Bangladesh,Ireland,Afghanistan")

participants = [p.strip() for p in participants_str.split(",") if p.strip()]

# Fetch rankings automatically
rankings = fetch_rankings(year, format_type)

# Add form rank inputs (auto-populate from fetched rankings)
st.write("Adjust Form Ranks (1=best, 20=worst; auto-fetched where possible)")
form_ranks = {}
for team in participants:
    auto_rank = rankings.get(team, default_rankings.get(team, 20))
    form_ranks[team] = st.slider(f"Form Rank for {team}", 1, 20, auto_rank)

# Add underdog selection
underdog_teams = st.multiselect("Select Underdog Teams for Karmic Boost (if karmic year)", participants)

if st.button("Predict Winner"):
    year_num = get_numerology(year)
    year_zod = get_zodiac(year)
    
    st.write(f"Year's Numerology Energy: {year_num}")
    st.write(f"Year's Chinese Zodiac: {year_zod}")
    
    scores = {}
    hosts = [h.strip().lower() for h in host.split(",") if h.strip()]
    for team in participants:
        is_host = team.lower() in hosts
        is_underdog = team in underdog_teams
        score = calculate_score(team, year_num, year_zod, year, host=is_host, form_rank=form_ranks[team], is_underdog=is_underdog)
        if score is not None:
            scores[team] = score
    
    if scores:
        # Apply filtering logic based on year type and special conditions
        karmic_years = [3, 7, 8, 11, 22, 33]
        threshold = 8 if year_num == 3 else (5 if year_num == 8 else 6)
        
        filtered_scores = {}
        for team, score in scores.items():
            data = teams_data[team]
            country_year = data["country"]
            country_num = get_numerology(country_year)
            country_zod = get_zodiac(country_year)
            has_zodiac_history = team in zodiac_history.get(year_zod, [])
            special_inclusion = year_num in karmic_years and country_zod == year_zod and has_zodiac_history
            karmic_match = country_num == year_num and year_num in karmic_years
            
            if score != -float('inf') and (form_ranks[team] <= threshold or special_inclusion or karmic_match):
                filtered_scores[team] = score
        
        if filtered_scores:
            predicted_winner = max(filtered_scores, key=filtered_scores.get)
            st.write(f"Predicted Winner: {predicted_winner}")
            st.write("Filtered Scores (higher is better; weak fits eliminated):")
            for team, score in sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{team}: {score}")
        else:
            st.write("No strong contenders after filtering; fallback to all scores.")
            predicted_winner = max(scores, key=scores.get)
            st.write(f"Predicted Winner: {predicted_winner}")
            st.write("All Scores:")
            for team, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{team}: {score}")
    else:
        st.write("No valid teams provided.")
