import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from pickle import dump, load
from time import sleep, time


epsilon = 0.75
decay = 0.9999
discount = 0.95
lr = 0.1
EPISODES = 25001
SHOW_EVERY = 5000
ITERATIONS = 100

layout = np.array([[0, 0, 0, 1, 0, 0],
                   [1, 0, 1, 1, 1, 0],
                   [0, 0, 1, 0, 0, 0],
                   [0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 1, 2]])

punishments = {0: -10, 1: -250, 2: 500}
colour = {0: (235, 235, 235), 1: (20, 20, 20), 2: (0, 225, 255)}

if True:
    q_table = np.zeros(layout.shape)
else:
    with open("FILENAME.pickle", "rb") as f:
        q_table = load(f)


class Agent:
    AROUND = [[0, -1], [1, 0], [0, 1], [-1, 0]]

    def __init__(self):
        self.x = 0
        self.y = 0

    def maxQ(self):
        maxQ = [0, -np.inf]
        for i, move in enumerate(self.AROUND):
            dx = self.x + move[0]
            dy = self.y + move[1]

            if 0 <= dx < layout.shape[1] and 0 <= dy < layout.shape[0]:
                q = q_table[dy, dx]
                if q > maxQ[1]:
                    maxQ = [i, q]

        return maxQ

    def move(self, action):
        move = self.AROUND[action]
        self.x += move[0]
        self.y += move[1]

    def staticMove(self, action, x, y):
        move = self.AROUND[action]
        x += move[0]
        y += move[1]
        return q_table[y, x]


rewards = []
for episode in range(EPISODES):
    agent = Agent()

    if episode % SHOW_EVERY == 0:
        print(f"Episode {episode}  |  Epsilon {epsilon}  |  Mean {np.mean(rewards[-SHOW_EVERY:])}")
        show = True
    else:
        show = False

    episode_reward = 0
    for iteration in range(ITERATIONS):
        obs = [agent.x, agent.y]

        if np.random.random() > epsilon:
            q = agent.maxQ()
            action = q[0]
            cQ = q[1]
        else:
            action = np.random.choice([i for i in range(4) if 0 <= agent.x+agent.AROUND[i][0] < layout.shape[1] and 0 <= agent.y+agent.AROUND[i][1] < layout.shape[0]])
            cQ = agent.staticMove(action, agent.x, agent.y)

        agent.move(action)

        reward = punishments[layout[agent.y, agent.x]]
        maxfQ = agent.maxQ()[1]

        if reward == punishments[2]:
            new_q = punishments[2]
        else:
            new_q = (1 - lr) * cQ + lr * (reward + discount * maxfQ)
        q_table[agent.y, agent.x] = new_q

        if show:
            env = np.zeros((layout.shape[0], layout.shape[1], 3), dtype=np.uint8)
            for j in range(layout.shape[0]):
                for i in range(layout.shape[1]):
                    env[j, i] = colour[layout[j, i]]
            env[agent.y, agent.x] = (0, 255, 0)
            img = Image.fromarray(env, "RGB")
            img = img.resize((400, 400), resample=Image.NEAREST)
            cv2.imshow("image", np.array(img))
            cv2.waitKey(50)
            sleep(0.050)
            if reward == punishments[2]:
                break

        episode_reward += reward

        if reward == punishments[2]:
            break

    rewards.append(episode_reward)
    if epsilon/decay >= 0.1:
        epsilon *= decay


moving_avr = np.convolve(rewards, np.ones((SHOW_EVERY, ))/SHOW_EVERY, mode="valid")

plt.plot([i for i in range(len(moving_avr))], moving_avr)
plt.ylabel(f"Reward {SHOW_EVERY}ma")
plt.xlabel("episode #")
plt.show()

with open(f"qtable-{int(time())}.pickle", "wb") as f:
    dump(q_table, f)

print(q_table)