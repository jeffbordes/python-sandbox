class Phrase:
    """
    Represents a phrase in the Phrase Hunter game.
    Handles displaying the phrase and checking letter guesses.
    """
    
    def __init__(self, phrase):
        """
        Initialize a Phrase object with the given phrase.
        
        Args:
            phrase: The phrase string to be guessed (converted to lowercase)
        """
        self.phrase = phrase.lower()
    
    def display(self, guesses):
        """
        Display the phrase with guessed letters visible and unguessed letters as underscores.
        Spaces between words remain visible. Prints directly to console.
        
        Args:
            guesses: A list of letters that have been guessed
        """
        for letter in self.phrase:
            if letter in guesses:
                # Show the letter (including spaces since " " is in guesses)
                print(f"{letter}", end=" ")
            else:
                # Show underscore for unguessed letters
                print("_", end=" ")
        # Print newline at the end
        print()
    
    def check_guess(self, guess):
        """
        Check if the given letter is in the phrase.
        
        Args:
            guess: The letter to check
        
        Returns:
            True if the letter is in the phrase, False otherwise
        """
        return guess.lower() in self.phrase
    
    def check_complete(self, guesses):
        """
        Check if the entire phrase has been guessed.
        
        Args:
            guesses: A list of letters that have been guessed
        
        Returns:
            True if all letters in the phrase have been guessed, False otherwise
        """
        for letter in self.phrase:
            # If any letter hasn't been guessed, phrase is not complete
            if letter not in guesses:
                return False
        return True
