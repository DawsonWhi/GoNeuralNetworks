# agent class for neural network that will learn how to play go by playing against itself
import random #for random actions for the a:gent

class Agent:
    def __init__(self):
        self.episodes = []
        self.states = {}
        self.new_episode()

    def new_episode(self):
        self.episodes = []
        self.color = random.randint(0,1) # randomly choose if playing black or white    
        self.score = 0
        self.opponent = Agent() # for now this is just another agent will probably need to be changed


    def end_episode(self): # where reward will be calculated for now give the agent no reward
        # -1 = Lose, 1 = Win
        reward = 0
        if self.score > self.opponent.score:
            reward = 1
        else:
            reward = -1
class State:
    def __init__(self, score):
        self.score = score
        self.estimate = 0.0
        self.outcome = 0

    class Action: 
        def __init__(self, action):
            self.action = action
            self.pi = 0.5 # policy 
            self.taken = 1

