import gym
import numpy as np

env = gym.make('FrozenLake-v0')

# Initialize table with all zeros
Q = np.zeros([env.observation_space.n, env.action_space.n])
# Set learning parameters
lr = .8
y = .95
num_episodes = 30

#create lists to contain total rewards and steps per episode
# jList = []
rewardList = []
for episode in range(num_episodes):
    # Reset environment and get first new observation
    state = env.reset()
    rewardAll = 0
    done = False
    step_num = 0
    
    # The Q-Table learning algorithm. Assume that within 99 steps we'll either
    # end up at the finish point, or dead.
    while step_num < 99:
        step_num += 1
        old_state = state
        
        # Choose an action by greedily (with noise) picking from Q table
        action = np.argmax(Q[state, :] + np.random.randn(1, env.action_space.n) * (1./(episode + 1)))
        
        # Get new state and reward from environment
        new_state, reward, done, _ = env.step(action)

        # Update Q-Table with new knowledge
        Q[state, action] = Q[state, action] + lr * (reward + y * np.max(Q[new_state,:]) - Q[state, action])
        rewardAll += reward

        # Set the current state to the new state
        state = new_state
        print("episode=", episode, ", step_num=", step_num, ", _=", str(_), ", old_state", str(old_state), ", new_state", str(new_state), ", action=", str(action),", done=", str(done), ", reward=", str(reward), ", rewardAll=", str(rewardAll))
        env.render()

        # Episode is done when new_state is a hole, or the finish position (15)
        if done == True:
            break

        print(Q)
    
    # End of this episode!
    #jList.append(j)
    rewardList.append(rewardAll)

print("Score over time: ",  str(sum(rewardList) / num_episodes))

print("Final Q-Table Values")
print(Q)