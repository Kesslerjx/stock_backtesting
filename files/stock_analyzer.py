from collections import Counter
from math import copysign, floor
import statistics

def print_list(list):
    for l in list:
        print(l)

# Finds the average dollar movement
# Needs daily data, not intraday
def get_avg_range(days):

    changes = []

    for day in days:
        change = abs(day.close - day.open)
        changes.append(change)
    
    return round(statistics.mean(changes),2)

# Finds the chance of the stock price going the opposite direction every n_days
# Goes based off the previous day
def get_opp_dir_chance(days, n_day):
    count   = 0
    correct = 0

    # Check if it's the right day to check
    # Get the current day different to find if green or red
    # Same thing for next day
    # If signs are different, then it went the opposite direction
    for index, day in enumerate(days):
        if index % n_day == 0:
            count        = count + 1
            current_day  = day.close - day.open
            previous_day = days[index-1].close - days[index-1].open
            different    = not(copysign(1, current_day) == copysign(1, previous_day))

            if different:
                    correct = correct + 1
    
    return round(correct/count*100, 2)

# Finds the best nday to use for the stock thats passed to it
# Returns a dict containing the n value and its chance
def get_best_nday(days, times=30):

    best_chance = None
    best_n      = None

    for n in range(1, times, 1):
        chance = get_opp_dir_chance(days, n)
        if best_n == None:
            best_n      = n
            best_chance = chance
        elif chance > best_chance:
            best_n      = n
            best_chance = chance

    d = dict()
    d['n']      = best_n
    d['chance'] = best_chance

    return d

# Returns a list of dictionaries that consist of the n_day value and it's chance
def map_best_ndays(days, times=30):
    n_chances = []
    for n in range(1, times+1, 1):
        d = dict()

        d['n']      = n
        d['chance'] = get_opp_dir_chance(days, n)

        n_chances.append(d)

    return n_chances

# Looks back n_days to determine a trend
# It will then trade based on that trend
# Counts all correct trades to determine chance
def trend_trade_chance_ndays(days: list, n_days: int):
    
    count   = 0
    correct = 0

    for index, day in enumerate(days):
        if index - n_days >= 0 and index < len(days)-1:
            count += 1
            trend = copysign(1, day.close - days[index-n_days].close)
            guess = copysign(1, days[index+1].close - days[index+1].open) # Next days candle
            if guess == trend:
                correct += 1
    
    chance      = round(correct/count*100, 2)
    result      = dict()
    result['n'] = n_days
    result['c'] = chance

    return result

# Will try times number of days to find the one with the best chance
# Returns a dict with the best result, and the result of every day
def best_trend_trade_chance(days: list, times: int=30):
    best_result = None
    results = []

    for n in range(1, times, 1):
        result = trend_trade_chance_ndays(days, n)
        results.append(result)
        if best_result == None or result['c'] > best_result['c']:
            best_result = result
    
    r = dict()
    r['best']    = best_result
    r['results'] = results

    return r

# Loops through each day to determine the type of candle
# If candles are the same it adds to number
# Once a candle is different, it logs the number and resets to 1
# At the end if finds the average
# That average is the average number of days before the stock will close in the opposite direction
def get_counter_data_from(days: list):
    num_list = []
    number   = 1

    for index, day in enumerate(days):
        candle = copysign(1, day.close - day.open)
        if index > 0:
            p_candle = copysign(1, days[index-1].close - days[index-1].open)
            if candle == p_candle:
                number += 1
            else:
                num_list.append(number)
                number = 1
        else:
            number += 1

    data = Counter(num_list)

    return data

# Uses the counter data that is calculated in the days_before_opp_dir function
def get_chance_from(values: list, value: int):

    total     = 0
    frequency = 0

    for data in values:
        total += values[data]
        if data == value:
            frequency = values[data]

    chance   = frequency / total
    inverted = 1 - chance
    result   = dict()

    result['chance']   = round(chance, 2)
    result['inverted'] = round(inverted, 2)

    return result
