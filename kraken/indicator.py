"""
Module with the different indicador implementations.
"""

import statistics


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
