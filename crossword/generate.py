import sys

from crossword import *





class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        '''I need to remove any variable in self.domains that is not the same length as a particular variable'''
        for variable in self.domains:
            for possible_word in self.domains[variable].copy():
                if len(possible_word) != variable.length:
                    self.domains[variable].remove(possible_word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        if self.crossword.overlaps[x,y] is not None:
            x_index, y_index = self.crossword.overlaps[x,y]

            for x_word in self.domains[x].copy():
                if any([x_word[x_index]==y_word[y_index] for y_word in self.domains[y]]):
                    revised = False

                else:                
                    self.domains[x].remove(x_word)
                    revised = True

        return revised
    

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            arcs = []
            for x in self.domains:
                for y in self.domains:
                    if x!=y:
                        arcs.append((x,y))
            
        while arcs:
            curr_x, curr_y = arcs.pop(0)
            if self.revise(curr_x, curr_y):
                for neighbor in self.crossword.neighbors(curr_x)-{curr_y}:
                    arcs.append((curr_x, neighbor))
                if len(self.domains[curr_x]) == 0:
                    return False
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        complete = False
        for element in self.domains:
            if element not in assignment.keys():
                return False
        if all([variable for variable in assignment]):
            complete=True
        return complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consistence = True
        values_list = list(assignment.values())
        values_set = set(list(assignment.values()))

        
        if len(values_list) != len(values_set):
            consistence = False
        
        for key, value in zip(assignment.keys(),assignment.values()):
            if len(value)!= key.length:
                consistence = False

        for value in assignment:
            for neighbor in  self.crossword.neighbors(value):
                if neighbor in assignment:
                    value_index, neighbor_index = self.crossword.overlaps[value, neighbor]
                    if assignment[value][value_index] != assignment[neighbor][neighbor_index]:
                        return False
                
        return consistence

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        '''we want to check how many neighbors of `var` contain some
        particular value we assign to `var`'''
        checker_dict = {}

        for item in self.domains[var]:
            count=0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                if item in self.domains[neighbor]:
                    count+=1
            checker_dict[item]=count

        return sorted(self.domains[var], key=lambda x: checker_dict[x])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        possible_returns = []
        possible_values = []
        for var in self.domains:
            var_values=set()
            if var not in assignment:
                possible_returns.append(var)
            for value in self.domains[var]:
                if value not in assignment.values():
                    var_values.add(value)
            possible_values.append(len(var_values))

        vars_remain_values = list(zip(possible_returns, possible_values))

        return min(vars_remain_values, key=lambda x: (x[1], len(self.crossword.neighbors(x[0]))))[0]  
            


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            assignment.update({var:value})
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            else:
                del assignment[var]
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
