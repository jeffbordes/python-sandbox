import random  # Importing the random module to generate random numbers


def start_game():
    """
    Main function for the Number Guessing Game.
    Includes game logic, user interaction, high score tracking, and replay functionality.
    """
    print("Welcome to the Number Guessing Game!")

    high_score = None  # Initialize the high score to None
    play_again = True  # Flag to determine if the player wants to play again

    while play_again:
        # Show the current high score
        if high_score is None:
            print("There is no high score yet. Set the first one!")
        else:
            print(f"The current high score is {high_score} attempts. Try to beat it!")

        # Generate a random number as the solution
        solution = random.randint(1, 100)
        attempts = 0  # Counter to track the number of attempts

        # Game loop: Continue until the player guesses correctly
        while True:
            try:
                # Prompt the player for their guess
                guess = int(input("Enter your guess (a number between 1 and 100): "))

                # Ensure the guess is within the valid range
                if guess < 1 or guess > 100:
                    print("Out of range! Please enter a number between 1 and 100.")
                    continue

                # Increment the attempt counter
                attempts += 1

                # Provide feedback: Too high, too low, or correct
                if guess < solution:
                    print("It's higher!")
                elif guess > solution:
                    print("It's lower!")
                else:
                    # Player guessed correctly
                    print(f"Congratulations! You've guessed the correct number in {attempts} attempts.")

                    # Update the high score if applicable
                    if high_score is None or attempts < high_score:
                        high_score = attempts
                        print("You've set a new high score!")
                    break
            except ValueError:
                # Handle invalid inputs gracefully
                print("Invalid input! Please enter a valid number between 1 and 100.")

        # Ask the player if they want to play again
        play_again_prompt = input("Would you like to play again? (Y/N): ").strip().upper()
        if play_again_prompt != 'Y':
            play_again = False

    # Goodbye message to signal the end of the game
    print("Thank you for playing! The game is now over.")


# Kick off the program by calling the start_game function
if __name__ == "__main__":
    start_game()