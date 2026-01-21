# Import the Game class from the phrasehunter package
from phrasehunter.game import Game


# Dunder Main statement - ensures the game only runs when this file is executed directly
if __name__ == "__main__":
    # Create an instance of the Game class
    game = Game()
    
    # Start the game by calling the start method
    game.start()
