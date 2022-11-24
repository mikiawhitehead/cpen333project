# Group#: G33
# Student Names: Emmanuel Santacruz, Mikia Whitehead

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self, queue, game):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self, queue, gui):
        self.queue = queue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self, queue):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = queue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15          # speed of snake updates (sec)
        # While the game is not over we continuously want the snake to move
        while self.gameNotOver:
            time.sleep(SPEED)   # This will set how fast we call the move method
            self.move()         # Call the move method

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        # Create Variables Needed For Method
        NewSnakeCoordinates = self.calculateNewCoordinates()                                                # New snake coordniates based on movements
        snakeSize = len(self.snakeCoordinates)                                                              # Lenght of the snake
        preyCoordinates = (gui.canvas.coords(gui.preyIcon)[0] + 5, gui.canvas.coords(gui.preyIcon)[1] + 5)  # Coordinates of the prey

        # Check wether the movent will lead to the capture of a prey
        if NewSnakeCoordinates == preyCoordinates:
            self.score += 1                                                                                 # Update the score
            self.snakeCoordinates.append(NewSnakeCoordinates)                                               # Append the new coordinates to the list, instead of the switching process
            self.createNewPrey()                                                                            # Create a new prey
            self.queue.put_nowait({"score": self.score})                                                    # Put task to update score in the queue
        # If the movement does not lead to the capture of a prey, then simply shift the snake coordinates acordingly
        # Since the body of the snake always follows the head, we simply have to move everything from Tail + 1 to Head - 1
        else:
            for i in range(snakeSize - 1):                                                                  # We disregard the location of the head which is why there is a -1. The new head of the snake will simply be the calculated coordinates
                self.snakeCoordinates[i] = (self.snakeCoordinates[i+1])                                     # The tail of the snake is at snakeCoordinates[0] so we go from [0:snakeSize - 1]
            self.snakeCoordinates[-1] = NewSnakeCoordinates                                                 # If as a result of the movement we do not cature a prey then simply move the head to to calculated coordinates
        # Check to see if the movement results in the end of the game
        self.isGameOver(self.snakeCoordinates)
        # Add the movement task into the queue
        self.queue.put_nowait({"move": self.snakeCoordinates})

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]    # Head of the snake
        direction = self.direction                  # Direction the snake is moving
        # Note that the snake has been defined in intervals of 10, since the gui.Icons have a width of 10, so we keep the same convention in our calculations
        
        if direction == "Up":                       # If direction is up we add 5 from the previous y-cord of the head of the snake
          return (lastX, lastY - 10)
        elif direction == "Down":                   # If direction is down we subtract 5 from the prevous y-cord of the head of the snake
          return(lastX, lastY + 10)  
        elif direction == "Left":                   # If direction is left we subtract 5 from the previous x-cord of the head of the snake
          return(lastX - 10, lastY)
        else:                                       # Else if direction is right we add 5 from the previous x-cord of the head of the snake
          return(lastX + 10, lastY)
        


    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        # Create Variables required for method
        headX, headY = snakeCoordinates[-1]                                             # The coordinates of the head of the snake
        snakeBody = len(snakeCoordinates) - 1                                           # Disregard the head of the snake

        if (headX,headY) in snakeCoordinates[0:snakeBody]:                              # If the coordinates of the snake's head are found somewhere else in the snake, then that means we have bit ourselves and the game should be over
            self.gameNotOver = False                                                    # Update game flag accordingly
            self.queue.put_nowait({"game_over"})                                        # Put a gameOver task in the queue
        elif headX < 0 or headY < 0 or headX > WINDOW_WIDTH or headY > WINDOW_HEIGHT:   # The game can also end if the head goes beyond the bounds of the window
            self.gameNotOver = False                                                    # Update game flag accordingly
            self.queue.put_nowait({"game_over"})                                        # Put a gameOver task in the queue
                
    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). 
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        # Create Variables Needed For Method
        THRESHOLD = 15                                                      #sets how close prey can be to borders
        preyX, preyY = (1,1)                                                # Variables we will check

        while (preyX % 10) != 5:                                            # Since the snake will move in steps of 10 units, and the snake starts in a 5 mod10 square, the coordinates of the snake will always be 5 mod 10 which we also want for our prey
            preyX = random.randint(0+THRESHOLD,WINDOW_WIDTH-THRESHOLD)      # Generate this 5 mod 10 number between the threshold boundary
        while (preyY % 10) != 5:
            preyY = random.randint(0+THRESHOLD, WINDOW_HEIGHT-THRESHOLD)    # Generate this 4 mod 10 number between the threshold boundary
        
        self.queue.put_nowait({"prey": (preyX - 5, preyY - 5, preyX + 5, preyY + 5)}) # Update queue to create a new prey


if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    
    BACKGROUND_COLOUR = "green"   #you may change this colour if you wish
    ICON_COLOUR = "black"        #you may change this colour if you wish

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game(gameQueue)        #instantiate the game object

    gui = Gui(gameQueue, game)    #instantiate the game user interface
    
    QueueHandler(gameQueue, gui)  #instantiate our queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()
    
