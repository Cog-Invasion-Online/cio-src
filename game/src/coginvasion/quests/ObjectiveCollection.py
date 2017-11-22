"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file ObjectiveCollection.py
@authors Maverick Liberty
@date November 13, 2017

@desc Essentially a list of objectives that works as a buffer and supports 'seeking'.

"""

class ObjectiveCollection:
    
    def __init__(self, *args):
        # Expecting to be passed subclasses of the Objective class.
        # This will be our cache of Objectives.
        self.cache = list(args)
        
        # The position of the 'seeker'.
        # MUST CALL #next() to obtain the next objective. 
        self.seeker = -1
        
    def append(self, objective):
        # Appends an objective to the end of the collection.
        self.cache.append(objective)
                
    def remove(self, objective):
        # Removes an objective from the collection and resets the position of the seeker.
        self.cache.remove(objective)
        self.seeker = -1
        
    def pop(self, objective):
        # Pops an objective from the collection, resets the position of the seeker, and returns the popped element.
        self.seeker = -1
        self.cache.pop(objective)
        
    def index(self, element):
        # Returns the index of the first occurrence of an element or -1 if not inside the list.
        return self.cache.index(element) if element in self.cache else -1
    
    def __getitem__(self, item):
        # This allows us to treat objects of this class like actual lists.
        return self.cache[item]
    
    def __len__(self):
        # This returns the length of the collection of objectives.
        return len(self.cache)
    
    def __contains__(self, element):
        # This returns if the element is inside of our cache.
        return element in self.cache
    
    def __iter__(self):
        # Yields all our objectives for iterations.
        for objective in self.cache:
            yield objective
    
    def nextObjective(self):
        # Revolving door #nextObjective() function that returns the next objective in relation to where the seeker is.
        # If the seeker is at the top of the list, the seeker will restart with the first element.
        # Returns the next objective in the collection in relation to the seeker.
        if self.seeker + 1 < len(self.cache):
            self.seeker += 1
        else:
            self.seeker = 0
        return self.seek()
    
    def seek(self):
        # Returns the objective at the position the seeker is at.
        if 0 <= self.seeker < len(self.cache):
            return self.cache[self.seeker]
        return None
    
    def lastObjective(self):
        # Revolving door #lastObjective() function that returns the objective in the position behind where the seeker is.
        # If the seeker is at the bottom of the list, the seeker will move to the top of the list.
        # Returns the previous objective in the collection in relation to the seeker.
        if self.seeker - 1 >= 0:
            self.seeker -= 1
        else:
            self.seeker = len(self.cache) - 1
        return self.seek()
        
    def isComplete(self):
        # Checks if all objectives in the collection are complete.
        complete = 0
        
        for objective in self.cache:
            if objective.isComplete():
                complete += 1
        
        return complete == len(self.cache)
    
    def clear(self):
        # Clears all the objectives within the collection and resets the seeker.
        self.cache = []
        self.seeker = -1
        
    def cleanup(self):
        # Clears and cleans up all attributes for garbage collection.
        self.clear()
        del self.cache
        del self.seeker
