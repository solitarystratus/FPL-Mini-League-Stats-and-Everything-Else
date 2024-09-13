import requests
import pandas as pd
import random

# League ID from user input
league_id = input('League ID')

# Function to get data from a particular page of the mini-league standings
def get_mini_league_data_page(league_id, page_number):
    url = f'https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/?page_new={page_number}'
    print(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        if 'standings' in data and 'results' in data['standings']:
            return data['standings']['results']
        else:
            print(f"Unexpected data structure: {data}")
            return []
    except requests.RequestException as e:
        print(f"Error fetching league data: {e}")
        return []

# Function to get manager name for a specific entry ID
def get_team_manager_name(entry_id):
    team_url = f'https://fantasy.premierleague.com/api/entry/{entry_id}/'
    try:
        response = requests.get(team_url)
        response.raise_for_status()  
        team_data = response.json()
        return team_data.get('player_first_name') + ' ' + team_data.get('player_last_name')
    except requests.RequestException as e:
        print(f"Error fetching manager data for {entry_id}: {e}")
        return "Unknown Manager"

# Fetch data from a random dummy page
page_number = 1
page_x_data = get_mini_league_data_page(league_id, page_number)

# Convert the data into a DataFrame
page_x_df = pd.DataFrame(page_x_data)

# Function to get gameweek points for a specific team (entry ID)
def get_team_gw_points(entry_id):
    team_url = f'https://fantasy.premierleague.com/api/entry/{entry_id}/history/'
    print(f"Fetching team data from URL: {team_url}")
    try:
        response = requests.get(team_url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json().get('current', [])
    except requests.RequestException as e:
        print(f"Error fetching team data for {entry_id}: {e}")
        return []

# Calculate the points for Gameweeks 1, 2, and 3 and the total points
def calculate_gw_points(entry_id):
    team_gw_data = get_team_gw_points(entry_id)
    if team_gw_data:
        gw_points = {gw['event']: gw['points'] for gw in team_gw_data}
        gw_1_points = gw_points.get(1, 0)
        gw_2_points = gw_points.get(2, 0)
        gw_3_points = gw_points.get(3, 0)
        total_points = sum(gw_points.values())
        gw_2_and_3_sum = gw_2_points + gw_3_points
        total_gw1_gw3_sum = gw_1_points + gw_2_points + gw_3_points
        return total_points, gw_1_points, gw_2_points, gw_3_points, gw_2_and_3_sum, total_gw1_gw3_sum
    else:
        return 0, 0, 0, 0, 0, 0

# Apply the function to calculate points and add new columns to the DataFrame
page_x_df[['Total_Points', 'GW_1_Points', 'GW_2_Points', 'GW_3_Points', 'GW_2_and_3_Sum', 'Total_GW1_GW3_Sum']] = page_x_df['entry'].apply(
    lambda entry_id: pd.Series(calculate_gw_points(entry_id))
)

# Add manager names to the DataFrame
page_x_df['manager_name'] = page_x_df['entry'].apply(lambda entry_id: get_team_manager_name(entry_id))

# Randomly shuffle DF and split it into random 1 vs 1 match
def generate_random_matchups(df, points_column, matchup_name):
    # Shuffle the DF rows 
    df_shuffled = df.sample(frac=1, random_state=random.randint(1, 1000)).reset_index(drop=True)
    
    # Ensure there is an even number of players; if odd, remove the last one
    if len(df_shuffled) % 2 != 0:
        df_shuffled = df_shuffled[:-1]
    
    matchups = []
    # Pair players after shuffling
    for i in range(0, len(df_shuffled), 2):
        manager1 = df_shuffled.loc[i, 'manager_name']
        manager2 = df_shuffled.loc[i + 1, 'manager_name']
        points1 = df_shuffled.loc[i, points_column]
        points2 = df_shuffled.loc[i + 1, points_column]
        
        # Determine winner and loser based on points
        if points1 > points2:
            winner, loser = manager1, manager2
        else:
            winner, loser = manager2, manager1
        
        matchups.append({
            'Manager1': manager1,
            'Manager2': manager2,
            f'{matchup_name}_Points1': points1,
            f'{matchup_name}_Points2': points2,
            f'{matchup_name}_Winner': winner,
            f'{matchup_name}_Loser': loser
        })
    
    return pd.DataFrame(matchups)

# Generate random 1 vs 1 pairing for GW2 + GW3 points
gw_2_3_matchups_df = generate_random_matchups(page_x_df, 'GW_2_and_3_Sum', 'GW2_GW3')

# Generate random 1 vs 1 pairing for total points across GW1, GW2, and GW3
total_gw1_gw3_matchups_df = generate_random_matchups(page_x_df, 'Total_GW1_GW3_Sum', 'Total_GW1_GW3')

# Save both the main data, GW2/GW3 matchups, and GW1/GW2/GW3 matchups to Excel
output_file = f'fpl_page_{page_number}_data_with_1v1pairing.xlsx'

try:
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        page_x_df.to_excel(writer, sheet_name='Player_Data', index=False)
        gw_2_3_matchups_df.to_excel(writer, sheet_name='GW2_GW3_1v1', index=False)
        total_gw1_gw3_matchups_df.to_excel(writer, sheet_name='Total_GW1_GW3_1v1', index=False)
    print(f"Data from page {page_number} with gameweek points and random matchups saved to {output_file}")
except Exception as e:
    print(f"Failed to save data to Excel: {e}")
