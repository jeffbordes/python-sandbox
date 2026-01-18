import copy

from constants import PLAYERS, TEAMS


def clean_data(players):
    """
    Clean player data without modifying the original.
    - Height: converted to integer (removes ' inches')
    - Experience: converted to boolean (True/False)
    - Guardians: converted from string to list (split on ' and ')
    """
    cleaned_players = copy.deepcopy(players)

    for player in cleaned_players:
        # Convert height from "42 inches" to 42
        player['height'] = int(player['height'].split()[0])

        # Convert experience from "YES"/"NO" to True/False
        player['experience'] = player['experience'].upper() == 'YES'

        # Convert guardians from string to list
        player['guardians'] = player['guardians'].split(" and ")

    return cleaned_players


def balance_teams(players, teams):
    """
    Distribute players evenly across all teams.
    Ensures each team has the same number of experienced and inexperienced players.
    Returns a dictionary with team names as keys and lists of players as values.
    """
    # Separate players by experience
    experienced = [player for player in players if player['experience']]
    inexperienced = [player for player in players if not player['experience']]
    
    # Calculate how many of each type per team
    exp_per_team = len(experienced) // len(teams)
    inexp_per_team = len(inexperienced) // len(teams)
    
    # Create a dictionary to hold each team's roster
    team_rosters = {team: [] for team in teams}
    
    # Distribute experienced players evenly
    for i, team in enumerate(teams):
        start = i * exp_per_team
        end = start + exp_per_team
        team_rosters[team].extend(experienced[start:end])
    
    # Distribute inexperienced players evenly
    for i, team in enumerate(teams):
        start = i * inexp_per_team
        end = start + inexp_per_team
        team_rosters[team].extend(inexperienced[start:end])
    
    return team_rosters


def display_menu():
    """Display the main menu options."""
    print("\n" + "=" * 40)
    print("       BASKETBALL TEAM STATS TOOL")
    print("=" * 40)
    print("\n---- MENU ----\n")
    print("  1) Display Team Stats")
    print("  2) Quit")
    print()


def display_team_stats(team_name, players):
    """Display stats for a single team in a readable format."""
    # Get player names as a comma-separated string
    player_names = ", ".join([player['name'] for player in players])
    
    # Count experienced and inexperienced players
    num_experienced = sum(1 for player in players if player['experience'])
    num_inexperienced = sum(1 for player in players if not player['experience'])
    
    # Calculate average height
    total_height = sum(player['height'] for player in players)
    avg_height = total_height / len(players)
    
    # Get all guardians as a comma-separated string
    all_guardians = []
    for player in players:
        all_guardians.extend(player['guardians'])
    guardians_string = ", ".join(all_guardians)
    
    # Display the stats
    print("\n" + "=" * 50)
    print(f"  Team: {team_name}")
    print("=" * 50)
    
    print(f"\n  Total Players: {len(players)}")
    print(f"  Experienced: {num_experienced}")
    print(f"  Inexperienced: {num_inexperienced}")
    print(f"  Average Height: {avg_height:.1f} inches")
    
    print(f"\n  Players:\n  {player_names}")
    
    print(f"\n  Guardians:\n  {guardians_string}")
    
    print("\n" + "-" * 50 + "\n")


def main():
    # Clean the player data
    cleaned_players = clean_data(PLAYERS)

    # Balance teams
    team_rosters = balance_teams(cleaned_players, TEAMS)

    while True:
        display_menu()

        choice = input("Enter an option (1 or 2): ")

        if choice == "1":
            print("\n---- SELECT A TEAM ----\n")
            for i, team in enumerate(TEAMS, 1):
                print(f"  {i}) {team}")
            print()

            team_choice = input("Enter team number: ")

            try:
                team_index = int(team_choice) - 1
                if 0 <= team_index < len(TEAMS):
                    team_name = TEAMS[team_index]
                    display_team_stats(team_name, team_rosters[team_name])
                    input("\nPress ENTER to continue...")
                else:
                    print("\n  Invalid team number!!! Please try again.\n")
            except ValueError:
                print("\n  Please enter a valid number!!!!\n")

        elif choice == "2":
            print("\n" + "=" * 40)
            print("  Thanks for using the Stats Tool!")
            print("  Goodbye!")
            print("=" * 40 + "\n")
            break
        else:
            print("\n  Invalid option. Please enter 1 or 2.\n")


if __name__ == "__main__":
    main()