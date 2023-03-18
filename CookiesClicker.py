"""
Cookie Clicker Simulator
"""
import math
import simpleplot

# Used to increase the timeout, if necessary
import codeskulptor

codeskulptor.set_timeout(20)

import poc_clicker_provided as provided

# Constants
SIM_TIME = 10000000000.0


class ClickerState:
    """
    Simple class to keep track of the game state.
    """

    def __init__(self):
        self._total_cookies = 0.0
        self._current_cookies = 0.0
        self._current_time = 0.0
        self._current_cps = 1.0
        self._item_name = None
        self._item_cost = 0.0
        self._history_list = [(self._current_cookies, self._item_name, self._item_cost, self._total_cookies)]
        self._time_until = 'inf'

    def __str__(self):
        """
        Return human readable state
        """
        return "\n" + "TotalCookies:" + str(self._total_cookies) + "\n" \
            + "CurrentCookies:" + str(self._current_cookies) + "\n" \
            + "CurrentTime:" + str(self._current_time) + "\n" \
            + "CurrentCPS:" + str(self._current_cps) + "\n"

    def get_cookies(self):
        """
        Return current number of cookies
        (not total number of cookies)

        Should return a float
        """
        return self._current_cookies

    def get_name(self):
        """
        Return current upgrade item name

        Should return None or a string
        """
        return self._item_name

    def get_cps(self):
        """
        Get current CPS

        Should return a float
        """
        return self._current_cps

    def get_time(self):
        """
        Get current time

        Should return a float
        """
        return self._current_time

    def get_history(self):
        """
        Return history list

        History list should be a list of tuples of the form:
        (time, item, cost of item, total cookies)

        For example: [(0.0, None, 0.0, 0.0)]

        Should return a copy of any internal data structures,
        so that they will not be modified outside of the class.
        """
        return self._history_list

    def time_until(self, cookies):
        """
        Return time until you have the given number of cookies
        (could be 0.0 if you already have enough cookies)

        Should return a float with no fractional part
        """
        if cookies <= self._current_cookies:
            self._time_until = 0.0
        else:
            self._time_until = math.ceil((cookies - self._current_cookies) / self._current_cps)
        return self._time_until

    def wait(self, time):
        """
        Wait for given amount of time and update state

        Should do nothing if time <= 0.0
        """
        if time > 0:
            self._current_time += time
            self._current_cookies += self._current_cps * time
            self._total_cookies += self._current_cps * time
        else:
            pass

    def buy_item(self, item_name, cost, additional_cps):
        """
        Buy an item and update state

        Should do nothing if you cannot afford the item
        """
        if self._current_cookies >= cost:
            self._item_name = item_name
            self._item_cost = cost
            self._current_cps += additional_cps
            self._current_cookies -= cost
            history_tuple = (self._current_time, self._item_name, self._item_cost, self._total_cookies)
            self._history_list.append(history_tuple)
        else:
            pass


def simulate_clicker(build_info, duration, strategy):
    """
    Function to run a Cookie Clicker game for the given
    duration with the given strategy.  Returns a ClickerState
    object corresponding to the final state of the game.
    """
    upgrade = build_info.clone()
    action = ClickerState()
    while action.get_time() <= duration:
        time_left = duration - action.get_time()
        item_name = action.get_name()
        item_name = strategy(action.get_cookies(), action.get_cps(), action._history_list, time_left, upgrade)
        if item_name == None:
            break
        if action.time_until(upgrade.get_cost(item_name)) > time_left:
            break
        else:
            item_name = strategy(action.get_cookies(), action.get_cps(), action._history_list, time_left, upgrade)
            action.wait(action.time_until(upgrade.get_cost(item_name)))
            action.buy_item(item_name, upgrade.get_cost(item_name), upgrade.get_cps(item_name))
            upgrade.update_item(item_name)
    action.wait(time_left)
    return action


def strategy_cursor(cookies, cps, history, time_left, build_info):
    """
    Always pick Cursor!

    Note that this simplistic (and broken) strategy does not properly
    check whether it can actually buy a Cursor in the time left.  Your
    simulate_clicker function must be able to deal with such broken
    strategies.  Further, your strategy functions must correctly check
    if you can buy the item in the time left and return None if you
    can't.
    """
    return "Cursor"


def strategy_none(cookies, cps, history, time_left, build_info):
    """
    Always return None

    This is a pointless strategy that will never buy anything, but
    that you can use to help debug your simulate_clicker function.
    """
    return None


def strategy_cheap(cookies, cps, history, time_left, build_info):
    """
    Always buy the cheapest item you can afford in the time left.
    """
    build_info_cheap = build_info.clone()
    item_cost_list = [build_info_cheap.get_cost(item) for item in build_info_cheap.build_items()]


def strategy_expensive(cookies, cps, history, time_left, build_info):
    """
    Always buy the most expensive item you can afford in the time left.
    """
    item_list = build_info.build_items()
    cost_list = map(build_info.get_cost, item_list)
    temp_list_item = []
    temp_list_cost = []
    for i in range(len(cost_list)):
        if cost_list[i] <= cookies + cps * time_left:
            temp_list_cost.append(cost_list[i])
            temp_list_item.append(item_list[i])
    if temp_list_cost == []:
        return None
    else:
        expensive_index = temp_list_cost.index(max(temp_list_cost))
        expensive_item = temp_list_item[expensive_index]
        return expensive_item


def strategy_best(cookies, cps, history, time_left, build_info):
    """
    The best strategy that you are able to implement.
    """
    item_list = build_info.build_items()
    cost_list = map(build_info.get_cost, item_list)
    cps_list = map(build_info.get_cps, item_list)
    eff_list = []
    for i in range(len(item_list)):
        efficiency = cps_list[i] / cost_list[i]
        eff_list.append(efficiency)
    most_eff_index = eff_list.index(max(eff_list))
    most_eff_item = item_list[most_eff_index]


def run_strategy(strategy_name, time, strategy):
    """
    Run a simulation for the given time with one strategy.
    """
    state = simulate_clicker(provided.BuildInfo(), time, strategy)
    print(strategy_name, ":", state)

    # Plot total cookies over time

    # Uncomment out the lines below to see a plot of total cookies vs. time
    # Be sure to allow popups, if you do want to see it

    history = state.get_history()
    history = [(item[0], item[3]) for item in history]
    # simpleplot.plot_lines(strategy_name, 1000, 400, 'Time', 'Total Cookies', [history], True)


def run():
    """
    Run the simulator.
    """
    run_strategy("Cursor", SIM_TIME, strategy_cursor)

    # Add calls to run_strategy to run additional strategies
    # run_strategy("Cheap", SIM_TIME, strategy_cheap)
    # run_strategy("Expensive", SIM_TIME, strategy_expensive)
    run_strategy("Best", SIM_TIME, strategy_best)


run()
