"""
Module with the different indicador implementations.
"""

import statistics
import sys


def sma(source, length):
    """
    Simple moving average.
    """
    series = []

    for i in range(0, len(source)):
        first = i - length + 1 if i >= length else 0
        series.append(statistics.mean(source[first:i + 1]))

    return series


def mom(source, length):
    """
    Momentum.
    """
    series = []

    for i in range(0, len(source)):
        first = i - length if i >= length else 0
        series.append(source[i] - source[first])

    return series

def rsi(source, length):
    """
    Relative strengh index.
    """
    change = [0] + [source[x] - source[x - 1] for x in range(1, len(source))]

    gain = [abs(x) if x > sys.float_info.epsilon else 0 for x in change]
    loss = [abs(x) if x < -sys.float_info.epsilon else 0 for x in change]

    avg_gain = [0] * length + [statistics.mean(gain[1:length + 1])]
    avg_loss = [0] * length + [statistics.mean(loss[1:length + 1])]

    for i in range(length + 1, len(source)):
        avg_gain.append((avg_gain[i - 1] * (length - 1) + gain[i]) / length)
        avg_loss.append((avg_loss[i - 1] * (length - 1) + loss[i]) / length)

    rs = [avg_gain[x]/avg_loss[x] if avg_loss[x] > sys.float_info.epsilon else 0 for x in range(0, len(avg_gain))]
    rsi = [100 - (100/(1 + rs[x])) for x in range(0, len(rs))]

    return rsi


if  __name__ == "__main__":
    source = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 46.08, 45.89, 46.03,
              45.61, 46.28, 46.28, 46.00, 46.03, 46.41, 46.22, 45.64, 46.21, 46.25, 45.71, 46.45,
              45.78, 45.35, 44.03, 44.18, 44.22, 44.57, 43.42, 42.66, 43.13]
    result = rsi(source, 14)
