from SpreadSheetClient import SpreadSheetClient
import sys

project = sys.argv[1]

# Call client
sheet = SpreadSheetClient(project)

# Test size edge case
sheet.size()

print()

# Provide examples of insert method
sheet.insert(99, 99, 100000)
sheet.insert(12, 56, [0, 4, 5])
sheet.insert(3, 6, "jack")
sheet.insert(5, 10, "carolina")
sheet.insert(3, 4, True)
sheet.insert(2, 8, "notre dame")
sheet.insert(7, 9, { 'food' : 'hot dog'})
sheet.insert(5, 10, "natalie")
sheet.insert(0, 0, "A")
sheet.insert(0, 1, "B")
sheet.insert(0, 2, "C")
sheet.insert(0, 3, "D")
sheet.insert(1, 0, "E")
sheet.insert(1, 1, "F")
sheet.insert(1, 2, "G")
sheet.insert(1, 3, "H")
sheet.insert(2, 0, "I")
sheet.insert(2, 1, "J")
sheet.insert(2, 2, "K")
sheet.insert(2, 3, "L")
sheet.insert(3, 0, "M")
sheet.insert(3, 1, "N")
sheet.insert(3, 2, "O")
sheet.insert(3, 3, "P")

print()

# Error checking for insert
sheet.insert(0, "dog", 0)
sheet.insert(3.4, 0, 0)
sheet.insert(-9, 0, -5)

print()

# Provide examples of lookup method
sheet.lookup(99, 99)    # Should return 100000
sheet.lookup(2, 8)      # Should return "notre dame"
sheet.lookup(3, 6)      # Should return "jack"
sheet.lookup(1, 2)      # Should return "G"
sheet.lookup(100, 100)  # Should return None
sheet.lookup(10, 20)    # Should return None

print()

# Error checking for lookup
sheet.lookup("two", "three")
sheet.lookup(4.3, 3.4)
sheet.lookup(-5, -3)

print()

# Provide examples for remove
sheet.remove(99, 99)
sheet.remove(5, 10)
sheet.remove(2, 0)
sheet.remove(5, 10)
sheet.remove(99,99)
sheet.remove(1000, 1000)

print()

# Error checking for remove
sheet.remove("dog", "cat")
sheet.remove(-5, -2)

print()

# More examples for testing size method
sheet.size()
sheet.remove(12, 56)
sheet.size()

print()

# testing query
sheet.query(0, 0, 5, 5)
sheet.query(1, 3, 1, 5)

print()

# Error checking for query
sheet.query(-1, 0, 3, 5)
sheet.query(1, 2, 0, 0)
sheet.query(0, 0, -2, "dog")
sheet.query(0, 6, "dog", 0)







