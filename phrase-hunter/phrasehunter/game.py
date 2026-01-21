import random
from phrasehunter.phrase import Phrase


class Game:
    """
    Manages the Phrase Hunter game logic including game state,
    user interaction, and win/loss conditions.
    """
    
    def __init__(self):
        """
        Initialize a new Game with default values.
        Sets up the phrase list and initializes game state.
        """
        # Track the number of incorrect guesses (game over at 5)
        self.missed = 0
        
        # List of Phrase objects to use in the game
        self.phrases = [
            Phrase("hello world"),
            Phrase("python is fun"),
            Phrase("practice makes perfect"),
            Phrase("keep it simple"),
            Phrase("never give up")
        ]
        
        # The current phrase being played
        self.active_phrase = self.get_random_phrase()
        
        # List of letters the user has guessed (starts with space so spaces display)
        self.guesses = [" "]
    
    def start(self):
        """
        Start the game loop.
        Displays welcome message, and runs the main game loop.
        Prompts to play again when game ends.
        """
        # Display welcome message
        self.welcome()
        
        # Main game loop - continues until win (phrase complete) or loss (5 misses)
        while self.missed < 5 and not self.active_phrase.check_complete(self.guesses):
            # Print the number of misses
            print(f"Number missed: {self.missed}")
            
            # Display the current state of the phrase
            self.active_phrase.display(self.guesses)
            
            # Get a guess from the user
            user_guess = self.get_guess()
            
            # Add the guess to the list of guesses
            self.guesses.append(user_guess)
            
            # Check if the guess is incorrect
            if not self.active_phrase.check_guess(user_guess):
                # Incorrect guess - increment missed counter
                self.missed += 1
        
        # Game has ended - show result
        self.game_over()
        
        # Ask if player wants to play again
        if self.play_again():
            self.reset()
            self.start()
        else:
            print("\nThanks for playing Phrase Hunter! Goodbye!")
    
    def reset(self):
        """
        Reset the game state for a new game.
        Clears guesses, resets missed counter, and selects new phrase.
        """
        self.missed = 0
        self.active_phrase = self.get_random_phrase()
        self.guesses = [" "]
    
    def get_random_phrase(self):
        """
        Randomly select and return a phrase from the phrases list.
        
        Returns:
            A randomly selected Phrase object
        """
        return random.choice(self.phrases)
    
    def welcome(self):
        """
        Display a friendly welcome message at the start of the game.
        """
        print("=" * 28)
        print("  Welcome to Phrase Hunter")
        print("=" * 28)
        print()
    
    def get_guess(self):
        """
        Prompt the user for a letter guess and validate the input.
        Ensures the guess is a single letter that hasn't been guessed before.
        Shows error messages for invalid input.
        
        Returns:
            A valid single letter guess (lowercase)
        """
        while True:
            guess = input("Enter a letter: ").lower().strip()
            
            # Validate that the input is exactly one character
            if len(guess) != 1:
                print("Error: Please enter exactly one character.")
                continue
            
            # Validate that the input is a letter (a-z)
            if not guess.isalpha():
                print("Error: Please enter a letter (a-z), not a number or symbol.")
                continue
            
            # Check if the letter has already been guessed
            if guess in self.guesses:
                print(f"You already guessed '{guess}'. Try a different letter.")
                continue
            
            return guess
    
    def game_over(self):
        """
        Display the end game message based on win or loss.
        Checks if missed equals 5 (loss) or phrase is complete (win).
        """
        if self.missed >= 5:
            print(f"\nYou lost! The phrase was: {self.active_phrase.phrase}")
        else:
            print("\nCongratulations! You won!")
    
    def play_again(self):
        """
        Prompt the player to play another game.
        
        Returns:
            True if the player wants to play again, False otherwise
        """
        while True:
            response = input("\nWould you like to play again? (yes/no): ").lower().strip()
            
            if response in ['yes', 'y']:
                print()
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'.")
