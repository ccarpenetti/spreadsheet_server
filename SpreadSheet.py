class SpreadSheet:

    def __init__(self):
        # Spreadsheet will be a dict with {(row, col) : value} key-value pairs
        self.table = dict()
    
    def insert(self, row, col, value): # insert the given value at the (row, col) key
        self.table[(row, col)] = value
        return True

    def lookup(self, row, col): # lookup value at a particular (row, col) key
        if (row, col) in self.table:
            return True, self.table[(row, col)]
        else:
            return True, f"No value in ({row}, {col})"
 
    def remove(self, row, col): # remove the value at the given (row, col) key
        if (row, col) in self.table:
            del self.table[(row, col)]
            return True
        else:
            return False

    def size(self): # return the max row and col values
       
        if len(self.table) == 0:
            return "There are no rows or columns in this table"
        else: 
            max_row = 0
            max_col = 0

            for (row, col) in self.table.keys():
                if row > max_row:
                    max_row = row
                if col > max_col:
                    max_col = col

            return (max_row + 1, max_col + 1) # (# of rows, # of cols)

    def query(self, start_row, start_col, width, height):

        result = {}

        end_row = start_row + width - 1
        end_col = start_col + height - 1

        # Iterate through all (row, col) combinations within row and column ranges
        # and create subset
        for curr_row in range(start_row, end_row + 1):
            row = {}
            for curr_col in range(start_col, end_col + 1):
                if (curr_row, curr_col) in self.table:
                    row[curr_col] = self.table[(curr_row, curr_col)]
                else:
                    row[curr_col] = None
            result[curr_row] = row

        return result
                    
