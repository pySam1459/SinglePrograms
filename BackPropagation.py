from pickle import dump, load, HIGHEST_PROTOCOL
from random import random, shuffle
from math import exp
from time import time
from datetime import datetime


class NeuralNetwork:
    learningRate = 0.02

    NEVER = 0
    ALL = 1
    RANDOM = 2

    def __init__(self, layout):
        self.layout = layout
        self.rLayout = layout[::-1]

        self.weights = [[[random()*2-1 for i in range(l1)] for j in range(l2)] for l1, l2 in zip(layout[:-1], layout[1:])]
        self.bias = [[random()*2-1 for i in range(l)] for l in layout[1:]]
        self.neurones = [[0.0 for i in range(l)] for l in layout]

        self.timeTaken = 0


    def sigmoid(self, z):
        return 1/(1 + exp(-z))

    def deriv_sigmoid(self, z):
        return z * (1 - z)


    def save(self):
        data = {"weights": self.weights, "bias": self.bias, "layout": self.layout, "learningRate": self.learningRate}
        name = str(datetime.now()).split(".")[0].replace(":", ",")
        with open(f"NeuralNetwork {name}.pkl", "wb") as file:
            dump(data, file, HIGHEST_PROTOCOL)
            print(f"Neural Network saved! Filename: NeuralNetwork {name}.pkl")

    def load(self, filename):
        with open(filename, "rb") as file:
            data = load(file)

        self.weights = data["weights"]
        self.bias = data["bias"]
        self.layout = data["layout"]
        self.learningRate = data["learningRate"]


    def forward(self, z):
        self.neurones[0] = z[:]
        for i, (weights, bias) in enumerate(zip(self.weights, self.bias), 1):
            z = [self.sigmoid(sum([weight * neurone for weight, neurone in zip(w, z)]) + b) for w, b in zip(weights, bias)]
            self.neurones[i] = z[:]

        return z

    def fit(self, data, labels, epochs=1, batch_size=-1, shuffle_data=True, show_progress=1):
        if show_progress:
            if batch_size == -1:
                sBatch = len(data)

            else:
                sBatch = batch_size

            print(f"Training has started : Data points {len(data)} | Epochs {epochs} | Batch Size {sBatch} | Data Shuffle {shuffle_data}")

        theTime = time()
        for epoch in range(epochs):
            if batch_size == -1:
                cost, taken = self.backPropagation(data, labels)
                if show_progress == self.ALL or (show_progress == self.RANDOM and random() > 0.995):
                    self.printProgress(taken, cost, -1, f"{epoch}/{epochs}")

            else:
                a = len(data) // batch_size

                for i in range(a):
                    cost, taken = self.backPropagation(data[i*batch_size:(i+1)*batch_size], labels[i*batch_size:(i+1)*batch_size])
                    if show_progress == self.ALL or (show_progress == self.RANDOM and random() > 0.995):
                        self.printProgress(taken, cost, a/len(data), f"{epoch}/{epochs}")

            if shuffle_data:
                array = [{"data": X, "target": Y} for X, Y in zip(data, labels)]
                shuffle(array)
                data, labels = [], []
                for item in array:
                    data.append(item["data"])
                    labels.append(item["target"])

        print(f"Time {time() - theTime}")

    def backPropagation(self, X, Y):
        startTime = time()
        changeWeights = [[[0 for i in range(l1)] for j in range(l2)] for l1, l2 in zip(self.layout[:-1], self.layout[1:])][::-1]
        changeBiases = [[0 for i in range(l)] for l in self.layout[1:]][::-1]
        cost = 0

        for data, target in zip(X, Y):
            yhat = self.forward(data)
            rNeurones = self.neurones[::-1]
            cost += sum([(a-b)**2 for a, b in zip(target, yhat)]) / len(yhat)

            delta = None
            for l, weights in enumerate(self.weights[::-1]):
                if l == 0:
                    delta = [(a - b) * self.deriv_sigmoid(b) for a, b in zip(target, yhat)]

                else:
                    pW = self.weights[::-1][l-1]
                    delta = [sum([pW[i][j] * d for i, d in enumerate(delta)]) * self.deriv_sigmoid(rNeurones[l][j]) for j in range(self.rLayout[l])]

                for j, (neurone, d) in enumerate(zip(changeWeights[l], delta)):
                    for i in range(self.rLayout[l+1]):
                        neurone[i] += d * rNeurones[l+1][i] * self.learningRate

                    changeBiases[l][j] += d * self.learningRate

        # Not this
        for weights, cWeights, bias, cBias in zip(self.weights, changeWeights[::-1], self.bias, changeBiases[::-1]):
            for j, (neurone, rNeurone) in enumerate(zip(weights, cWeights)):
                for i in range(len(neurone)):
                    neurone[i] += rNeurone[i]

                bias[j] += cBias[j]

        return cost, time() - startTime


    def printProgress(self, theTime, cost, amount, epoch):
        if amount == -1:
            progress = "=============>>"

        else:
            x = int(15*amount)
            if x > 1:
                progress = "="*(x-2) + ">>" + "."*(15-x)

            else:
                progress = ">" + "."*(15-x)

        print(f"  ~ Epochs: {epoch}  |  Data Fitted: [{progress}]  |  Cost: {cost}  |  Time Taken: {theTime}")

    def final(self, X, Y, show_data=False):
        print("\nResults - ")
        cost = 0

        for data, target in zip(X, Y):
            yhat = self.forward(data)
            cost += sum([(a - b)**2 for a, b in zip(target, yhat)])/(2 * len(yhat))

            if show_data:
                print(f"  ~ Data: {data}  |  Target: {target}  |  Prediction: {yhat}")

            else:
                print(f"  ~ Target: {target}  |  Prediction: {yhat}")

        print(f"  ~ Final Cost: {cost}\n")


def main():
    data = [[0, 0], [0, 1], [1, 0], [1, 1]]
    labels = [[0], [0], [0], [1]]

    nn = NeuralNetwork([2, 1])
    nn.fit(data, labels, 20000, -1, True, NeuralNetwork.RANDOM)

    nn.final(data, labels, True)


if __name__ == '__main__':
    main()
