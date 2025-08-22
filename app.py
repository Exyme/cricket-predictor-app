import streamlit as st

# Dictionary of teams with their test status year and country foundation year
teams_data = {
    "Australia": {"test": 1877, "country": 1901},
    "England": {"test": 1877, "country": 1707},
    "South Africa": {"test": 1889, "country": 1910},
    "West Indies": {"test": 1928, "country": 1958},
    "New Zealand": {"test": 1930, "country": 1907},
    "India": {"test": 1932, "country": 1947},
    "Pakistan": {"test": 1952, "country": 1947},
    "Sri Lanka": {"test": 1982, "country": 1948},
    "Zimbabwe": {"test": 1992, "country": 1980},
    "Bangladesh": {"test": 2000, "country": 1971},
    "Ireland": {"test": 2018, "country": 1922},
    "Afghanistan": {"test": 2018, "country": 1919},
}

# Chinese zodiac animals based on year % 12
zodiac_animals = ["Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig", "Rat", "Ox", "Tiger", "Rabbit"]

# Zodiac groups (allies)
zodiac_groups = {
    "group1": ["Rat", "Dragon", "Monkey"],
    "group2": ["Ox", "Snake", "Rooster"],
    "group3": ["Tiger", "Horse", "Dog"],
    "group4": ["Rabbit", "Goat", "Pig"],
}

# Secret friends
secret_friends = {
    "Rat": "Ox", "Ox": "Rat",
    "Tiger": "Pig", "Pig": "Tiger",
    "Rabbit": "Dog", "Dog": "Rabbit",
    "Dragon": "Rooster", "Rooster": "Dragon",
    "Snake": "Monkey", "Monkey": "Snake",
    "Horse": "Goat", "Goat": "Horse",
}

# Enemies (opposites)
enemies = {
    "Rat": "Horse", "Horse": "Rat",
    "Ox": "Goat", "Goat": "Ox",
    "Tiger": "Monkey", "Monkey": "Tiger",
    "Rabbit": "Rooster", "Rooster": "Rabbit",
    "Dragon": "Dog", "Dog": "Dragon",
    "Snake": "Pig", "Pig": "Snake",
}

# Friendly and enemy numbers from Vedic numerology (approximation based on common tables)
friendly = {
    1: [1, 2, 3, 5, 6, 9],
    2: [1, 2, 3, 5],
    3: [1, 2, 3, 5, 7],
    4: [1, 5, 7, 6],
    5: [1, 2, 3, 5, 6, 9],
    6: [1, 3, 5, 6, 9],
    7: [1, 2, 4, 5, 7],  # Adjusted to match the method's example for 7
    8: [1, 2, 5, 6],
    9: [1, 2, 3, 5, 6, 9],
    11: [1, 2, 3, 5, 6, 9],  # Treat as amplified 2
    22: [1, 5, 7, 6],  # Treat as amplified 4
    33: [1, 3, 5, 6, 9],  # Treat as amplified 6
}

enemy_nums = {
    1: [8],
    2: [8, 4, 9],
    3: [6],
    4: [2, 9],
    5: [],
    6: [2, 4, 7],
    7: [3, 6, 8, 9],  # Adjusted to match the method's example for 7
    8: [3, 4, 7, 9],
    9: [4, 7, 8],
    11: [8, 4, 9],  # As 2
    22: [2, 9],  # As 4
    33: [2, 4, 7],  # As 6
}

def get_numerology(year):
    s = sum(int(d) for d in str(year))
    while s > 9 and s not in [11, 22, 33]:
        s = sum(int(d) for d in str(s))
    return s

def get_zodiac(year):
    index = year % 12
    return zodiac_animals[index]

def get_group(animal):
    for group, members in zodiac_groups.items():
        if animal in members:
            return members
    return []

def calculate_score(team, year_num, year_zod, host=False):
    if team not in teams_data:
        return None
    
    data = teams_data[team]
    test_year = data["test"]
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
    
    # Zodiac score (team weighted more)
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
        zod_score += 1.5
    if secret_friends.get(country_zod) == year_zod:
        zod_score += 1.5
    if country_zod in get_group(year_zod) and country_zod != year_zod:
        zod_score += 1
    if enemies.get(country_zod) == year_zod:
        zod_score -= 1.5
    else:
        zod_score += 0.5  # neutral
    
    total_score = num_score + zod_score
    
    # Prioritize numerology if karmic/master year
    if year_num in [3, 7, 11, 22, 33]:
        total_score += num_score * 0.5  # Extra weight
    
    # Host boost if no double penalty
    if host and not double_penalty:
        total_score += 2
    
    # Disqualify if double penalty unless exact match
    if double_penalty and team_num != year_num:
        total_score = -float('inf')
    
    return total_score

# Streamlit app
st.title("Cricket World Cup Winner Predictor")
st.write("Based on Refined Vedic Numerology and Chinese Astrology Method. This is for fun and interpretive purposes only.")

year = st.number_input("World Cup Year", min_value=1900, max_value=2100, value=2023)
format_type = st.selectbox("Cricket Format", ["ODI", "T20", "Test/WTC"])
host = st.text_input("Host Team (optional)")
participants_str = st.text_input("Participants (comma-separated, e.g., India,Australia,England)", value="Australia,England,South Africa,West Indies,New Zealand,India,Pakistan,Sri Lanka,Zimbabwe,Bangladesh,Ireland,Afghanistan")

participants = [p.strip() for p in participants_str.split(",") if p.strip()]

if st.button("Predict Winner"):
    year_num = get_numerology(year)
    year_zod = get_zodiac(year)
    
    st.write(f"Year's Numerology Energy: {year_num}")
    st.write(f"Year's Chinese Zodiac: {year_zod}")
    
    scores = {}
    for team in participants:
        score = calculate_score(team, year_num, year_zod, host.lower() == team.lower())
        if score is not None:
            scores[team] = score
    
    if scores:
        predicted_winner = max(scores, key=scores.get)
        st.write(f"Predicted Winner: {predicted_winner}")
        st.write("Scores:")
        for team, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            st.write(f"{team}: {score}")
    else:
        st.write("No valid teams provided.")
