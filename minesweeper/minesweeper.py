import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # Initializes empty set to store known mines
        mines = set()

        # Checks if the number of cells in the set of cells equals the number of mines in set of cells
        if len(self.cells) == self.count:

            # If true then loops over each cell in self.cells
            for cell in self.cells:

                # Adds each cell to mines
                mines.add(cell)

        # Returns set of known mines for current set of cells
        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # Intializes empty set to store known safe cells
        safe = set()

        # Checks if the number of mines in set of cells equals 0
        if self.count == 0:

            # If true then loops over each cell in self.cells
            for cell in self.cells:

                # Adds each cell to safe
                safe.add(cell)

        # Returns set of known safe cells for current set of cells
        return safe

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # Checks if cell known to be a mine is in current set of cells
        if cell in self.cells:

            # If true then remove cell from sentence
            self.cells.remove(cell)

            # And reduce count of mines by 1
            self.count -= 1

            # Return True to exit function
            return 1

        # Else return False
        else:

            return 0

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """

        # Checks if cell known to be safe is in current set of cells
        if cell in self.cells:

            # If true then remove cell from sentence
            self.cells.remove(cell)

            # Return True to exit function
            return 1

        # Else return False
        else:

            return 0


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Adds safe cell to set of moves made
        self.moves_made.add(cell)

        # Adds safe cell to set of safe cells
        if cell not in self.safes:

            self.mark_safe(cell)

        # Intializes empty list to store surrounding cells
        current_knowledge_cells = []

        # Loops through the surrounding cells of the initial cell
        for i in range(cell[0] - 1, cell[0] + 2):

            for j in range(cell[1] - 1, cell[1] + 2):

                # Checks if current cell is the initial cell
                if (i, j) == cell:

                    # If so then skip over current iteration
                    continue

                # Else checks if cell falls within the boundaries of the game board
                elif 0 <= i < self.height and 0 <= j < self.width:

                    # If so then checks if cell is in moves_made or safes
                    if not (i, j) in (self.moves_made and self.safes):

                        # If false then add cell to current_knowledge_cells
                        current_knowledge_cells.append((i, j))

        # Checks if there are cells in current_knowledge_cells
        if len(current_knowledge_cells) != 0:

            # If there are, then create a new sentence using those cells and add them to the knowledge base
            self.knowledge.append(Sentence(current_knowledge_cells, count))

        # Loops through each sentence in the knowledge and determines what can be minimized
        for sentence in self.knowledge:

            # Initilaizes variables for known states of cells
            known_safes = sentence.known_safes()

            known_mines = sentence.known_mines()

            # Checks if known_safes is not empty
            if known_safes:

                # If so then update self.safes with known safes
                self.safes.update(known_safes)

                # Then rmove sentence from knowledge
                self.knowledge.remove(sentence)

            # Checks if known_mines is not empty
            if known_mines:

                # If so then remove sentence from knowledge
                self.knowledge.remove(sentence)

                # Loops through all known mines
                for mine in known_mines.union(self.mines):

                    # Marks them all as mines
                    self.mark_mine(mine)

        # print statements to keep track of AI moves, knowledge base, and confirmed mines
        print("\n\n\n\n")

        print("------------------------------------------------------------------")

        print("\nMove: ", cell)

        print("Knowledge Base:")

        for sentence in self.knowledge:

            print(sentence)

        print("\nConfirmed Mines:")

        print(self.mines," \n")

        print("------------------------------------------------------------------")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Initializes safe_moves to a copy of the set self.safes
        safe_moves = self.safes.copy()

        # Removes moves_made from safe_moves
        safe_moves -= self.moves_made

        # Checks if there are no safe moves
        if len(safe_moves) == 0:

            # If so then return none
            return None

        # Else randomly return one of the safe moves
        else:

            return safe_moves.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Check if there are no more possible moves
        if len(self.moves_made) == 56:

            # If so then return none
            return None

        # Intializes random_move to a random cell on the game board
        random_move = (random.randrange(self.height), random.randrange(self.width))

        # Initializes not_safe_moves to all unique cells in moves_made and mines
        not_safe_moves = self.moves_made | self.mines

        # Keeps generating random moves until it picks one not in not_safe_moves
        while random_move in not_safe_moves:

            random_move = (random.randrange(self.height), random.randrange(self.width))

        # Returns the random move
        return random_move