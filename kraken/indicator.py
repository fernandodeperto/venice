import statistics
import sys


def sma(source, length):
    series = []

    for i in range(0, len(source)):
        first = i - length + 1 if i >= length else 0
        series.append(statistics.mean(source[first:i + 1]))

    return series


def mom(source, length):
    series = []

    for i in range(0, len(source)):
        first = i - length if i >= length else 0
        series.append(source[i] - source[first])

    return series


def rsi(source, length):
    change = [0] + [source[x] - source[x - 1] for x in range(1, len(source))]

    gain = [abs(x) if x > sys.float_info.epsilon else 0 for x in change]
    loss = [abs(x) if x < -sys.float_info.epsilon else 0 for x in change]

    avg_gain = [0] * length + [statistics.mean(gain[1:length + 1])]
    avg_loss = [0] * length + [statistics.mean(loss[1:length + 1])]

    for i in range(length + 1, len(source)):
        avg_gain.append((avg_gain[i - 1] * (length - 1) + gain[i]) / length)
        avg_loss.append((avg_loss[i - 1] * (length - 1) + loss[i]) / length)

    rel_strength = [avg_gain[x]/avg_loss[x] if avg_loss[x] > sys.float_info.epsilon else 0 for x in
                    range(0, len(avg_gain))]

    return [100 - (100/(1 + rel_strength[x])) for x in range(0, len(rel_strength))]
