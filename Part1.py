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
            # We fixed the race condition caused by the sleep method by adding the following code
            # fast_input_semaphore.aquire()
            time.sleep(SPEED)   # This will set how fast we call the move method
            # fast_input_semaphore.release()
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
        # We can make this a bit more efficient by: (currentDirection == "Left" or currentDirection == "Right") and (e.keysym == "Right" or e.keysym == "Left") or (currentDirection == "Down" or currentDirection == "Up") and (e.keysym == "Down" or e.keysym == "Up")
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return    
        # We fixed the race condition here by adding the following code:
        # if fast_input_semaphore.aquire():
        self.direction = e.keysym
        #   fast_input_semaphore.release()

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
        # Check to see if the new coordinates satisfy over condition
        self.isGameOver(NewSnakeCoordinates)
        preyCoordinates = (gui.canvas.coords(gui.preyIcon)[0] + 5, gui.canvas.coords(gui.preyIcon)[1] + 5)  # Coordinates of the prey
        # Check wether the movent will lead to the capture of a prey
        if NewSnakeCoordinates == preyCoordinates:
            self.score += 1                                                                                 # Update the score
            self.queue.put_nowait({"score": self.score})                                                    # Put task to update score in the queue
            self.snakeCoordinates.append(NewSnakeCoordinates)                                               # Append the new coordinates to the list, instead of the switching process
            self.createNewPrey()                                                                            # Create a new prey
        # If the movement does not lead to the capture of a prey, then simply shift the snake coordinates acordingly
        # Since the body of the snake always follows the head, we simply have to move everything from Tail + 1 to Head - 1
        else:
            self.snakeCoordinates.append(NewSnakeCoordinates)
            self.snakeCoordinates.remove(self.snakeCoordinates[0])
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
        newCoordinates = (0,0)    
        # Note that the snake has been defined in intervals of 10, since the gui.Icons have a width of 10, so we keep the same convention in our calculations
        if direction == "Up":                       # If direction is up we add 5 from the previous y-cord of the head of the snake
          newCoordinates = (lastX, lastY - 10)
        elif direction == "Down":                   # If direction is down we subtract 5 from the prevous y-cord of the head of the snake
          newCoordinates = (lastX, lastY + 10)  
        elif direction == "Left":                   # If direction is left we subtract 5 from the previous x-cord of the head of the snake
          newCoordinates = (lastX - 10, lastY)
        else:                                       # Else if direction is right we add 5 from the previous x-cord of the head of the snake
          newCoordinates = (lastX + 10, lastY)
        return newCoordinates


    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates

        if (x,y) in self.snakeCoordinates[2:] or (x < 0) or (x > WINDOW_WIDTH) or (y < 0) or (y > WINDOW_HEIGHT):
          self.gameNotOver = False
          self.queue.put_nowait({"game_over": True})


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
            preyY = random.randint(0+THRESHOLD, WINDOW_HEIGHT-THRESHOLD)    # Generate this 5 mod 10 number between the threshold boundary
        
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
    
    fast_input_lock = threading.Lock()

    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()
    
