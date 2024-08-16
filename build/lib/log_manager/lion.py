from collections import defaultdict
from heapq import heappush, heappop

class Q1:
    def __init__(self, elephants, schedule):
        # map of our elephants' names to their sizes
        self.sizeMap = {elephant: size for elephant,size in elephants}
        # elephants of mine that are present at any given time
        self.mine = set()

        # we have to ignore our elephants entering and leaving
        # because we flush them independently, this keeps track
        self.ignoreMap = defaultdict(int)
        
        # other elephants that are present (max heap by size)
        self.others = []
        # elephants that have left but are still in the heap (lazy deletion)
        self.othersLeft = defaultdict(int) 

        # schedule sorted by time of arrival/leaving
        self.schedule = []
        for event in schedule:
            name, arrival, departure = event
            self.schedule.append((name, arrival, "arrive"))
            self.schedule.append((name, departure, "depart"))
            self.ignoreMap[(self.sizeMap[name], arrival, "arrival")] += 1
            self.ignoreMap[(self.sizeMap[name], departure, "departure")] += 1


        self.schedule.sort(key = lambda t: t[1])
        # schedule index
        self.si = 0

    def elephantEntered(self, time, height):
        key = (height, time, "arrival")
        if self.ignoreMap[key] > 0:
            self.ignoreMap[key] -= 1
        else:
            heappush(self.others, -height)

    def elephantLeft(self, time, height):
        key = (height, time, "departure")
        if self.ignoreMap[key] > 0:
            self.ignoreMap[key] -= 1
        else:
            self.othersLeft[height] += 1

    def getBiggestElephants(self, time):
        # flush my set of elephants to the ones that 
        # are currently in the room based on time
        while self.si < len(self.schedule) and self.schedule[self.si][1] <= time:
            name, _, type = self.schedule[self.si]
            if type == "arrive":
                self.mine.add((name, self.sizeMap[name]))
            else:
                self.mine.remove((name, self.sizeMap[name]))
            self.si += 1

        # flush the heap of other elephants to find the 
        # one who is the tallest and still present
        while self.others:
            cur = abs(self.others[0])
            if self.othersLeft[cur] > 0:
                heappop(self.others)
                self.othersLeft[cur] -= 1
            else:
                break

        tallestRival = abs(self.others[0])
        candidates = [name for name,height in self.mine if height >= tallestRival]
        candidates.sort()
        return candidates

sol = Q1([("marry", 300), ("rob", 250)], [("marry", 10, 15), ("rob", 13, 20)])
sol.elephantEntered(8, 200)
sol.elephantEntered(10, 310)
sol.elephantEntered(10, 300)
print(sol.getBiggestElephants(11))
sol.elephantEntered(13, 250)
sol.elephantLeft(13, 310)
print(sol.getBiggestElephants(13))
sol.elephantLeft(15, 300)
print(sol.getBiggestElephants(16))
sol.elephantLeft(16, 310)
sol.elephantLeft(20, 310)