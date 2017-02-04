import Tkinter as tk
import Map
import Agent

root = tk.Tk()



map = Map.Map(root,12)
agent = Agent.Agent(map)

#agent.test_baseline_agent(root)


for i in range(20):
    #agent.train_agent(root,"Supervised")
    agent.train_agent(root,"Reinforced")
    agent.test_agent(root)



root.mainloop()