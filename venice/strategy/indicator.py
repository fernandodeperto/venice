import sys

from decimal import Decimal

from venice.util import decimal_div


def sma(source, length):
    return [sum(source[x - length + 1:x + 1]) / length if x >= length else
            sum(source[0:x + 1]) / length for x in range(0, len(source))]


def mom(source, length):
    return [source[x] - source[x - length] if x >= length else source[x] - source[0] for x in
            range(0, len(source))]


def rsi(source, length):
    change = [Decimal(0)] + [source[x] - source[x - 1] for x in range(1, len(source))]

    gain = [abs(x) if x > sys.float_info.epsilon else Decimal(0) for x in change]
    loss = [abs(x) if x < -sys.float_info.epsilon else Decimal(0) for x in change]

    avg_gain = [Decimal(0)] * length + [sum(gain[1:length + 1]) / length]
    avg_loss = [Decimal(0)] * length + [sum(loss[1:length + 1]) / length]

    for i in range(length + 1, len(source)):
        avg_gain.append((avg_gain[i - 1] * (length - 1) + gain[i]) / length)
        avg_loss.append((avg_loss[i - 1] * (length - 1) + loss[i]) / length)

    rel_strength = [
        avg_gain[x]/avg_loss[x] if avg_loss[x] > sys.float_info.epsilon
        else Decimal(0) for x in range(0, len(avg_gain))]

    return [100 - (100/(1 + rel_strength[x])) for x in range(0, len(rel_strength))]


def crossover(source, source2):
    if isinstance(source2, list):
        return source[-2] <= source2[-2] and source[-1] > source2[-1]

    return source[-2] <= source2 and source[-1] > source2


def crossunder(source, source2):
    if isinstance(source2, list):
        return source[-2] >= source2[-2] and source[-1] < source2[-1]

    return source[-2] >= source2 and source[-1] < source2
