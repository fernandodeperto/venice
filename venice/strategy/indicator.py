import sys

from decimal import Decimal
# from logging import getLogger


def sma(source, length):
    return [sum(source[x - length + 1:x + 1]) / length if x >= length else
            sum(source[0:x + 1]) / length for x in range(0, len(source))]


def ema(source, length):
    result = [sum(source[0:length]) / length]
    multiplier = Decimal(2) / Decimal(length + 1)

    for i in range(length, len(source)):
        result.append(source[i] * multiplier + result[i-length] * (1 - multiplier))

    return result


def macd(fast_length, slow_length, source, signal_length):
    # logger = getLogger(__name__)

    fast_ema = ema(source, fast_length)
    slow_ema = ema(source, slow_length)

    fast_ema = fast_ema[len(fast_ema) - len(slow_ema):]

    macd_ = [fast_ema[i] - slow_ema[i] for i in range(0, len(slow_ema))]
    signal = ema(macd_, signal_length)

    macd_ = macd_[len(macd_) - len(signal):]

    histogram = [macd_[i] - signal[i] for i in range(0, len(signal))]

    # logger.debug('fast_ema={:.5f}, slow_ema={:.5f}, macd={:.5f}, signal={:.5f}, '
    #              'hist={:.5f}'.format(fast_ema[-1], slow_ema[-1], macd_[-1], signal[-1],
    #                                   histogram[-1]))

    return macd_, signal, histogram


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
