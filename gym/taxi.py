import gym
import numpy as np

env = gym.make('Taxi-v2')

# Initialize table with all zeros
Q = np.zeros([env.observation_space.n, env.action_space.n])

# Set learning parameters.
lr = 0.85  # Learning rate
gamma = 0.99
num_episodes = 1  # AKA number of times to play.

# Create lists to contain total rewards and steps per episode.
numsteps_list = []
reward_list = []
 
for episode in range(num_episodes):
    
    # Reset environment and get first new observation.
    state = env.reset()
    reward_total = 0  # Total reward so far
    done = False  # Is the game 'done'?
    step_num = 0  # We have taken 'j' steps.
    
    # The Q-Table learning algorithm.
    while step_num < 99:
        step_num += 1
        old_state = state
        
        # Choose an action by greedily (with noise) picking from Q table.
        # Note that the noise decreases with num. games played.
        action = np.argmax(Q[state] + np.random.randn(1, env.action_space.n)*(1./(episode+1)))
        
        # Get new state, reward, 'done' from environment.
        new_state, reward, done, _ = env.step(action)
        
        # Update Q-Table with new knowledge according to Bellman.
        Q[state, action] += lr*(reward + gamma*np.max(Q[new_state]) - Q[state, action])
        reward_total += reward

        # Set the current state to the new state
        state = new_state
        print("episode=", episode, ", step_num=", step_num, ", _=", str(_), ", old_state", str(old_state), ", new_state", str(new_state), ", action=", str(action),", done=", str(done), ", reward=", str(reward))
        env.render()


        # What makes an episode done?
        if done is True:
            break
    numsteps_list.append(step_num)  # Total number of steps
    reward_list.append(reward_total)  # Total reward
 
print 'Score over time: %s' % (np.average(reward_list))
print 'Score over last half: %s' % (np.average(reward_list[1000:]))