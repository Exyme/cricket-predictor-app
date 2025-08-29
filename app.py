Suggested Code Upgrades
Here are targeted code changes to implement the new rules. I'll provide snippets with minimal modifications for clarity—integrate them into the existing code (e.g., in calculate_score and the prediction block). Use consistent indentation and test with 1996/1999+ inputs to verify.

1. Update calculate_score Function (Add Maturity and Enhanced Underdog Boosts)
Add these lines after existing boosts (e.g., after form_boost and underdog lines):

python
Copy
# New Rule 2: Maturity Cycle Boost
years_since_country = year - data["country"]
mat_num = get_numerology(years_since_country)
if mat_num == 3 and year_num in karmic_years:
    total_score += 5

# New Rule 3: Enhanced Underdog Boost in Matching Zodiac Years
country_zod = get_zodiac(country_year)  # Already calculated, but ensure it's available
if is_underdog and country_zod == year_zod and year_num in karmic_years:
    total_score += 1  # Additional +1 on top of existing +2, making it +3 total
(Note: The existing underdog boost is +2; this adds +1 more for a net +3 under the condition.)

2. Update the Prediction Block (Relaxed Filtering)
Modify the filtered_scores creation (after calculating scores):

python
Copy
# Existing karmic_years definition (ensure it's global or defined)
karmic_years = [3, 7, 8, 11, 22, 33]

# Existing threshold
threshold = 8 if year_num == 3 else (5 if year_num == 8 else 6)

# Updated filtered_scores with New Rule 1
filtered_scores = {}
for team, score in scores.items():
    data = teams_data[team]
    country_year = data["country"]
    country_zod = get_zodiac(country_year)
    has_zodiac_history = team in zodiac_history.get(year_zod, [])
    special_inclusion = year_num in karmic_years and country_zod == year_zod and has_zodiac_history
    if score != -float('inf') and (form_ranks[team] <= threshold or special_inclusion):
        filtered_scores[team] = score
Additional Recommendations
Testing: Add a debug mode in Streamlit to log scores/thresholds for verification (e.g., st.write(f"Debug: {team} score={score}, included={team in filtered_scores}")).
User Input Enhancement: Add a tooltip for underdog selection: "Select for karmic underdog boosts in matching zodiac years."
Edge Cases: If no teams qualify after filtering, fallback to all scores (as existing). This ensures robustness.
No Breaking Changes: These are additive; they won't affect non-karmic/non-matching scenarios.
These upgrades capture the PDF's cosmic insights while keeping the code's spirit intact. If you provide specific test inputs or more details, I can refine further!
