import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys

class Dart:
    def __init__(self, abc=False):
        if not abc:
            self.names = ["Øystein", "Petter", "Jacob", "F9", "Kristian",
                "Erlend", "Carl", "Andy", "Maso"]
        elif abc:
            self.names = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.teams = [" Erlend | Øystein | Kristian ",
                      " Petter | Henrik | Andreas",
                      " Jacob | Maso | Carl "]
        self.pts_single = {}
        for name in self.names:
            self.pts_single[name] = 0
        self.pts_double = {}
        for team in self.teams:
            self.pts_double[team] = 0
        self.init_pair_count()
        # other
        self._semier = None
    
    # ------------------------------------------------------------------

    def semi_finals(self):
        """
        Creating a dictionary containing the semi-finals per round of
        the dart season of 22/23

        Order of names:
        Øystein, Petter, Jacob, F9, Kristian, Erlend, Carl, Andy, Maso

        Returns
        -------
        dict
            See docstring
        """
        self.rounds = {}
        self.indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.add_semi_finals(1)
        self.indices = [0, 3, 6, 1, 4, 7, 2, 5, 8]
        self.add_semi_finals(2)
        self.indices = [0, 4, 8, 1, 5, 6, 2, 3, 7]
        self.add_semi_finals(3)
        self.indices = [0, 5, 7, 2, 4, 6, 1, 3, 8]
        self.add_semi_finals(4)
        self.indices = [0, 7, 2, 5, 8, 1, 6, 4, 3]
        self.add_semi_finals(5)
        self.indices = [8, 7, 4, 6, 5, 0, 3, 1, 2]
        self.add_semi_finals(6)
        self.indices = [2, 8, 6, 3, 7, 5, 4, 1, 0]
        self.add_semi_finals(7)
        self.indices = [1, 7, 6, 0, 3, 8, 2, 5, 4]
        self.add_semi_finals(8)
        self.indices = [1, 2, 6, 8, 7, 5, 0, 4, 3]
        self.add_semi_finals(9)
        self.indices = [2, 7, 4, 8, 6, 3, 0, 5, 1]
        self.add_semi_finals(10)
        self.indices = [2, 8, 0, 1, 7, 3, 4, 6, 5]
        self.add_semi_finals(11)
        self.indices = [8, 1, 4, 0, 6, 7, 2, 5, 3]
        self.add_semi_finals(12)
    
    # ------------------------------------------------------------------

    def add_semi_finals(self, runde):
        names = self.names.copy()
        new_names = []
        for i in range(3):
            ind = self.indices[(3 * i):(3 * i + 3)]
            new_names.append([names[ind[0]], names[ind[1]], names[ind[2]]])
        self.rounds[runde] = [new_names[0], new_names[1], new_names[2]]
    
    # ------------------------------------------------------------------

    def count_pairs(self, print_results=False):
        """
        Counts how many times members have faced each other in the semi-
        finals; both two-by-two and three-by-three

        Parameters
        ----------
        rounds : dict
            dictionary containing the semi-finals per round of any dart
            season
        """
        self.semi_finals()
        for runde in self.rounds:
            counted = []
            semier = self.rounds[runde]
            for semi in semier:
                triple = sorted(semi)
                for name1 in triple:
                    for name2 in triple:
                        if name1 == name2:
                            continue
                        pair = " - ".join(sorted((name1, name2)))
                        if pair in counted:
                            continue
                        self.pair_count[pair] += 1
                        counted.append(pair)
                triple = " - ".join(triple)
                self.triple_count[triple] += 1
        serie_txt = "22_23"
        pickle_semis = open(f"../series/pickled_serie_{serie_txt}",
            "wb")
        pickle.dump(self.rounds, pickle_semis)
        pickle_semis.close()
        if print_results:
            self.print_counts()
    
    # ------------------------------------------------------------------

    def scoring(self):
        """
        Order of names in pts_singles:
        Øystein, Petter, Jacob, F9, Kristian, Erlend, Carl, Andy, Maso
        
        Order of teams in pts_doubles:
        (Erlend, Øystein, Kristian)
        (Petter, Henrik, Andreas)
        (Jacob, Maso, Carl)
        """
        singles = [[5, 1, 2, 2, 4, 1, 2, 3, 1],
                   [5, 2, 4, 1, 3, 1, 2, 1, 2],
                   [2, 1, 1, 5, 4, 3, 2, 2, 1]]
        doubles = [[3, 2, 1],
                   [2, 1, 3],
                   [3, 2, 1]]
        for pts in singles:
            for i, name in enumerate(self.names):
                self.pts_single[name] += pts[i]
        title = "SINGLES LEADERBOARD"
        print("\n\n\n\n" + "#" * 31)
        print(f"#{title:^29}#")
        print("#" * 31)
        print("#" + " " * 29 + "#")
        counter = 0
        for name, pts in sorted(
            self.pts_single.items(), key=lambda item: item[1], reverse=True):
            if counter == 3 or counter == 6:
                print("# " + "-" * 27 + " #")
            print(f"#{name:^14}:{pts:>9}" + " " * 5 + "#")
            counter += 1
        print("#" + " " * 29 + "#")
        print("#" * 31, "\n\n")

        for pts in doubles:
            for i, team in enumerate(self.teams):
                self.pts_double[team] += pts[i]
        title = "TEAMS LEADERBOARD"
        print("\n\n" + "#" * 41)
        print(f"#{title:^39}#")
        print("#" * 41)
        print("#" + " " * 39 + "#")
        for team, pts in sorted(
            self.pts_double.items(), key=lambda item: item[1], reverse=True):
            print(f"#{team:^31}:{pts:^7}#")
        # for team in self.teams:
        #     print(f"#{team:^31}:{self.pts_double[team]:^7}#")
        print("#" + " " * 39 + "#")
        print("#" * 41, "\n\n\n\n")
    
    # ------------------------------------------------------------------

    def init_pair_count(self):
        pair_count = {}
        triple_count = {}
        for name in self.names:
            for name_2nd in self.names:
                if name == name_2nd:
                    continue
                pair = sorted((name, name_2nd))
                pair = " - ".join(pair)
                if pair in pair_count.keys():
                    pass
                else:
                    pair_count[pair] = 0
                for name_3rd in self.names:
                    if name == name_3rd or name_2nd == name_3rd:
                        continue
                    triple = sorted((name, name_2nd, name_3rd))
                    triple = " - ".join(triple)
                    if triple in triple_count.keys():
                        continue
                    triple_count[triple] = 0
        self.pair_count = pair_count
        self.triple_count = triple_count
    
    # ------------------------------------------------------------------

    def print_counts(self):
        n_pair = 0
        _1st_name = "andy"
        title = "COUNTING PAIRS"
        print("\n\n\n\n" + "#" * 33)
        print(f"#{title:^31}#")
        print("#" * 33)
        print("#" + " " * 31 + "#")
        for pair, counts in sorted(
            self.pair_count.items(), key=lambda item: item[0]):
            if pair.split()[0] != _1st_name:
                print("# " + 29 * "-" + " #")
                _1st_name = pair.split()[0]
            n_pair += 1
            print(f"#{pair:^22}: {counts:^7}#")
        print("#" + " " * 31 + "#")
        print("#" * 33)
        print()
        n_triple = 0
        _1st_name = "andy"
        title = "COUNTING TRIPLES"
        print("\n" + "#" * 41)
        print(f"#{title:^39}#")
        print("#" * 41)
        print("#" + " " * 39 + "#")
        for team, counts in sorted(
            self.triple_count.items(), key=lambda item: item[0]):
            if team.split()[0] != _1st_name:
                print("# " + 37 * "-" + " #")
                _1st_name = team.split()[0]
            n_triple += 1
            print(f"#{team:^31}:{counts:^7}#")
        print("#" + 39 * " " + "#")
        print(41 * "#")
        print(f"\n\n#{n_pair = :^7}\t{n_triple = :^7}#\n\n\n\n")
    
    # ------------------------------------------------------------------

    def print_rounds(self):
        self.semi_finals()
        print("\n\n\n")
        for runde in self.rounds:
            title = f"Runde {runde}"
            print("#" * 40)
            print(f"#{title:^38}#")
            print("#" * 40)
            print("#" + " " * 38 + "#")
            tmp = self.rounds[runde]
            for i in range(len(tmp)):
                print(f"#{tmp[0][i]:^12}|{tmp[1][i]:^12}|{tmp[2][i]:^12}#")
            print("#" + " " * 38 + "#")
            print("#" * 40, "\n")
    
    # ------------------------------------------------------------------

    def dash(self):
        """
        Generating semi-finals with dashes as frame
        """
        self.semi_finals()
        print("\n\n\n")
        dash = "_"
        title = "SEMI-FINALS"
        print("#" * 40)
        print(f"#{title:^38}#")
        print("#" * 40, "\n")
        for runde in self.rounds:
            title = f"Round {runde}"
            title = f"|{title:^14}|"
            print(f"{16 * dash:^40}")
            print(f"{title:^40}")
            print("-" * 40)
            print("|" + " " * 12 + "|" + " " * 12 + "|" + " " * 12 + "|")
            tmp = self.rounds[runde]
            for i in range(len(tmp)):
                print(f"|{tmp[0][i]:^12}|{tmp[1][i]:^12}|{tmp[2][i]:^12}|")
            print("|" + " " * 12 + "|" + " " * 12 + "|" + " " * 12 + "|")
            print("-" * 40)
    
    # ------------------------------------------------------------------

    def hash(self):
        """
        Generating semi-finals with hashes as frame
        """
        self.semi_finals()
        print("\n\n\n")
        hash = "#"
        title = "SEMI-FINALS"
        print("#" * 40)
        print(f"#{title:^38}#")
        print("#" * 40, "\n")
        for runde in self.rounds:
            title = f"Round {runde}"
            # print("#" * 40)
            # print(f"#{title:^38}#")
            title = f"#{title:^14}#"
            print(f"{16 * hash:^40}")
            print(f"{title:^40}")
            print("#" * 40)
            print("#" + " " * 12 + "|" + " " * 12 + "|" + " " * 12 + "#")
            tmp = self.rounds[runde]
            for i in range(len(tmp)):
                print(f"#{tmp[0][i]:^12}|{tmp[1][i]:^12}|{tmp[2][i]:^12}#")
            print("#" + " " * 12 + "|" + " " * 12 + "|" + " " * 12 + "#")
            print("#" * 40, "\n")

def main(arg):
    boolt, boolf = (True, False)
    abc = boolf
    ode = Dart(abc=abc)
    if arg == "print semi-finals":
        # args[0]
        # ode.print_rounds()
        ode.dash()
        # ode.hash()
    elif arg == "count semi-final pairs":
        # args[1]
        ode.count_pairs()
    elif arg == "print score table":
        # args[2]
        ode.scoring()
    elif arg == "generate semi-finals":
        # args[3]
        ode.generate_semi_finals(5)

if __name__ == "__main__":
    args = ["print semi-finals",
            "count semi-final pairs",
            "print score table"]
    main(arg=args[1])