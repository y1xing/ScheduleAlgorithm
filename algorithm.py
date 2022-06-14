import sys
import itertools
import pandas as pd


def get_best_outcomes(solutions):

    score_list = [solution["score"] for solution in solutions]

    score_list.sort(key=float)
    best_schedules = [
        solution for solution in solutions if solution["score"] == score_list[0]]

    return best_schedules


# Define the structure of a node
class Node():
    def __init__(self, state, parent):
        # State is a pandas dataframe and the date [df, 1]
        self.state = state
        self.parent = parent
        # action is giving duty to N people and moving to the next date if N amount of duty is given
        # self.action = action


class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        # Used to check if state parameter (from neighbours/possible actions) is in the frontier
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            # Removes the last node in the frontier and then define the new frontier without it
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node


class QueueFrontier(StackFrontier):

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            # Removes the first node in the frontier
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node


class ScheduleAlgo():

    def __init__(self, unique_id):

        # Extract the information like days all those from database
        self.unique_id = unique_id

        # Format it to get the initial state
        """
        Will need to get the commitments, and then format it into the initial state
        Get the consecutive days, duty personel per day, rest day
        
        """
        # Testing Code
        self.start = (pd.read_csv("sampleData.csv", index_col=0), 1)
        print("-------Initial Df---------")
        print(self.start)

        parameters = {
            "CONSECUTIVE DAYS": 2,
            "DUTY PERSONEL PER DAY": 2,
            "REST DAY": 1.
        }

        self.days, self.dp_per_day, self.rest_day = parameters.values()
        self.last_day = int(self.start[0].columns[-1])

        self.solution = []

        # self.goal is when the last day has been filled up

    def terminal_state(self, state):
        df, date = state
        print(f"Terminal State: {date - 1} and {self.last_day}")
        return date - 1 == self.last_day

    def get_fairness_score(self, state):
        df, date = state
        # Calculate ths score of state
        no_of_duties = {}

        for name in list(df.index):
            no_of_duties[name] = list(df.loc[name].values).count("O")

        sum = 0
        for key, value in no_of_duties.items():
            sum += value

        avg = sum / len(no_of_duties)
        score = 0
        for key, value in no_of_duties.items():
            score += abs(value - avg)

        return round(score, 1)

    # Neighbours function returns the results of the all the possible actions from a state

    def neighbors(self, state):
        print(f"Inputed state is {state}")
        df, date = state
        results = []
        if date > self.last_day:
            return results

        target_col = df[str(date)]

        number_of_O = list(target_col.values).count("O")

        if number_of_O == self.dp_per_day:
            print("Have 2 O already")
            results.append((df, date + 1))
            return results
        else:
            # Need to add multiple conditions
            if date >= self.last_day:
                available_slots = target_col[target_col.isnull()].index
                combinations = list(itertools.combinations(
                    available_slots, self.dp_per_day))
                print(f"Combinations that exists is {combinations}")

                for names in combinations:
                    # action = f"{' '.join(names)} duty on {date}"
                    # print(action)
                    new_df = df.copy()

                    new_df.loc[names, str(date)] = "O"

                    results.append((new_df, date + 1))

                    return results

            else:
                available_slots = target_col[target_col.isnull()].index
                combinations = list(itertools.combinations(
                    available_slots, self.dp_per_day))
                print(
                    f"Combinationss that exists for {date} is {combinations}")

                new_combination = []
                for names in combinations:
                    # If one of the names is unable to do 2 consecutive duty due to "X", remove from combination
                    for name in names:
                        should_add = True
                        for i in range(self.days):
                            if df.loc[name][str(date + i)] == "X":
                                should_add = False
                        if not should_add:
                            break

                    if should_add:
                        new_combination.append(names)

                # Means cannot find any solution for this state, return empty frontier
                if len(new_combination) == 0:
                    print("EMPTY NEW COMBINATION, CANNOT WORK")
                    return results

                print(f"New combination is {new_combination}")
                results = []
                for names in new_combination:
                    # action = f"{' '.join(names)} duty on {date}"
                    new_df = df.copy()

                    current_date = date
                    for i in range(self.days):
                        if date + i >= self.last_day:
                            break
                        else:
                            new_df.loc[names, str(date + i)] = "O"

                    current_date = current_date + self.days
                    if current_date >= self.last_day:
                        pass
                    else:
                        for name in names:
                            for i in range(int(self.rest_day)):
                                if current_date + i >= self.last_day:
                                    print("It reached here 3")
                                    break
                                else:
                                    next_day = new_df.loc[name][str(
                                        current_date + i)]
                                    if next_day == "X":
                                        print("Is a X")
                                    else:
                                        new_df.loc[name, str(
                                            current_date + i)] = "Rest"
                    results.append((new_df, date + 1))

                x = {}
                for result in results:
                    score = self.get_fairness_score(result)

                    x[score] = result
                    # print(x)

                results2 = []
                for key in sorted(x)[-2:]:
                    results2.append(x[key])

                return results2

    def solve(self):
        """Finds a solution to maze, if one exists."""

        # Keep track of number of states explored
        self.num_explored = 0

        # Initialize frontier to just the starting position
        start = Node(state=self.start, parent=None)
        frontier = QueueFrontier()
        frontier.add(start)

        # Initialize an empty explored set
        # self.explored = set()

        # Keep looping until solution found
        while True:

            # If nothing left in frontier, then no path
            if frontier.empty():
                print("frontier is empty empty empty empty")
                return self.solution

            # Choose a node from the frontier
            node = frontier.remove()
            # if node.state[1] > self.last_day:
            #   return self.solution
            self.num_explored += 1

            # If node is the goal, append it to the solutions list
            if self.terminal_state(node.state):
                self.solution.append(
                    {"score": self.get_fairness_score(node.state),
                     "state": node.state}
                )
                # return

            # Mark node as explored
            # self.explored.add(node.state)

            # Add neighbors to frontier
            for state in self.neighbors(node.state):
                # If state in neighbour does not exist in the froniter and is the explored
                # if not frontier.contains_state(state) and state not in self.explored:
                child = Node(state=state, parent=node)
                frontier.add(child)
