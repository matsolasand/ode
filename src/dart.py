import numpy as np
import matplotlib.pyplot as plt
import pickle
import time
import sys
import os

class Dart:
    path_series = "../series/"
    path_scoring = "../scoring/"
    path_pair_counts = "../pair_counts/"
    def __init__(self, serie, verbose=False, desperate=False):
        self.serie = serie
        self.names = ["Øystein", "Petter", "Jacob", "F9", "Kristian",
            "Erlend", "Carl", "Andy", "Maso"]
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
        self.verbose = verbose
        self.desperate = desperate
        self.rounds = {}
        self._semier = None
    
    # ------------------------------------------------------------------

    def generate_semi_finals(self, runde, initiate=True):
        """
        Function for generating random semi-finals.
        Will pickle the series to the series-folder; this will happen if
        counting of and counting of triples are fine, i.e., only
        generating the least played pairs and semifinals.

        Parameters
        ----------
        runde  :  int
            The starting number of the runde that the semi-finals will
            be made for
        """
        if initiate:
            self.n_recursive = 0
            self.counter_10 = 0
        self.desperate_test = False
        self.n_recursive += 1
        serie_now = self.serie.replace("/", "_")
        self.__check_series(serie_now)
        self.__confirm_previous_series_counted(serie_now)
        self.__get_previous_series_counts(serie_now)
        self.indices = np.arange(9)
        roundices = {}
        counters = {}
        while runde <= 12:
            time_now = time.time()
            round_found = [False]
            counter = 0
            if runde < 10:
                timer = 0.05
            else:
                timer = 0.6
            while not round_found[0]:
                if np.abs(time.time() - time_now) > timer:
                    if runde >= 10:
                        self.counter_10 += counter
                        print(f"number of loops = {counter} (for {runde = })")
                    self.generate_semi_finals(runde=1, initiate=False)
                np.random.shuffle(self.indices)
                counter += 1
                if not self.desperate_test:
                    self.__test_semi_finals(round_found)
                else:
                    self.__desperate_semi_finals(round_found)
            roundices[runde] = self.indices.copy()
            self.__add_semi_finals(runde)
            self.__count_pairs_append()
            counters[runde] = counter
            if self.desperate:
                if runde >= 10:
                    self.desperate_test = True
                    print(f"total number of loops for 10 = {self.counter_10}")
                    print(runde)
            runde += 1
        for runde in roundices:
            self.indices = roundices[runde].copy()
            self.__add_semi_finals(runde)
        filename = self.path_series + f"pickled_serie_{serie_now}"
        pickle_semis = open(filename, "wb")
        pickle.dump(self.rounds, pickle_semis)
        pickle_semis.close()
        if self.verbose:
            print(counters)
    
    # ------------------------------------------------------------------

    def __check_series(self, serie_now):
        serie_now = serie_now.split("_")
        series_played = os.listdir(self.path_series)
        for series in series_played:
            if ".txt" in series:
                continue
            # series = "pickled_serie_yr_yr_final"
            serie_txt = series.split("_")[2:4]
            if serie_txt == serie_now:
                print("\nSemifinals for this series are already generated!")
                print(f"{self.serie = }")
                sys.exit()
    
    # ------------------------------------------------------------------

    def __confirm_previous_series_counted(self, serie_now):
        previous_series = False
        series_counted = os.listdir(self.path_pair_counts)
        nums = serie_now.split("_")
        now = [eval(num) for num in nums]
        for ff in series_counted:
            nums_ff = ff.split("_")[-2:]
            prev = [eval(num_ff) for num_ff in nums_ff]
            if (prev[0] == (now[0] - 1)) and (prev[1] == (now[0])):
                previous_series = True
                break
        if not previous_series:
            print("previous year's semifinals has not been counted!")
            sys.exit()
    
    # ------------------------------------------------------------------

    def __get_previous_series_counts(self, serie_now):
        nums = serie_now.split("_")
        serie_prev = "_".join([str(eval(num) - 1) for num in nums])
        filename = self.path_pair_counts + f"pickled_counts_{serie_prev}"
        pickled_counts = open(filename, "rb")
        all_counts = pickle.load(pickled_counts)
        self.pair_count = all_counts["pair"]
        self.triple_count = all_counts["triple"]
        pickled_counts.close()
    
    # ------------------------------------------------------------------

    def __test_semi_finals(self, test_ok):
        """
        Testing if the semi-finals randomly found is approved
        """
        names = self.names.copy()
        new_names = []
        for i in range(3):
            ind = self.indices[(3 * i):(3 * i + 3)]
            new_names.append([names[ind[0]], names[ind[1]], names[ind[2]]])
        semier = [new_names[0], new_names[1], new_names[2]]

        pair_min = min(self.pair_count.values())
        triple_min = min(self.triple_count.values())
        breaking = False
        for semi in semier:
            if breaking:
                break
            triple = sorted(semi)
            for name1 in triple:
                for name2 in triple:
                    if name1 == name2:
                        continue
                    pair = " - ".join(sorted((name1, name2)))
                    if self.pair_count[pair] > pair_min:
                        breaking = True
            triple = " - ".join(triple)
            if self.triple_count[triple] > triple_min:
                breaking = True
        if not breaking:
            self._semier = semier.copy()
            test_ok[0] = True
    
    # ------------------------------------------------------------------

    def __desperate_semi_finals(self, test_ok):
        """
        Testing if the semi-finals randomly found is approved (with
        desperate measures)
        """
        names = self.names.copy()
        new_names = []
        for i in range(3):
            ind = self.indices[(3 * i):(3 * i + 3)]
            new_names.append([names[ind[0]], names[ind[1]], names[ind[2]]])
        semier = [new_names[0], new_names[1], new_names[2]]

        pair_min = min(self.pair_count.values())
        triple_min = min(self.triple_count.values())
        breaking = False
        for semi in semier:
            if breaking:
                break
            pair_counter = 0
            triple = sorted(semi)
            for name1 in triple:
                for name2 in triple:
                    if name1 == name2:
                        continue
                    pair = " - ".join(sorted((name1, name2)))
                    if self.pair_count[pair] > (pair_min + 1):
                        breaking = True
                    elif self.pair_count[pair] > pair_min:
                        pair_counter += 1
            if pair_counter > 2:
                breaking = True
            triple = " - ".join(triple)
            if self.triple_count[triple] > triple_min:
                breaking = True
        if not breaking:
            self._semier = semier.copy()
            test_ok[0] = True
    
    # ------------------------------------------------------------------

    def __add_semi_finals(self, runde):
        names = self.names.copy()
        new_names = []
        for i in range(3):
            ind = self.indices[(3 * i):(3 * i + 3)]
            new_names.append([names[ind[0]], names[ind[1]], names[ind[2]]])
        self.rounds[runde] = [new_names[0], new_names[1], new_names[2]]
    
    # ------------------------------------------------------------------

    def __count_pairs_append(self):
        """
        Counts how many times members have faced each other in the semi-
        finals; both two-by-two and three-by-three

        Parameters
        ----------
        rounds : dict
            dictionary containing the semi-finals per round of any dart
            season
        """
        counted = []
        for semi in self._semier:
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
                   [2, 1, 2, 5, 4, 3, 2, 1, 1],
                   [2, 2, 4, 5, 1, 1, 2, 3, 1],
                   [2, 2, 1, 5, 1, 1, 2, 4, 3],
                   [2, 1, 2, 5, 4, 1, 3, 2, 1]]
        # may be wrong!
        doubles = [[3, 2, 1],
                   [2, 1, 3],
                   [2, 3, 1],
                   [2, 1, 3],
                   [1, 3, 2],
                   [2, 1, 3]]
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

    def print_counts(self, counts_done=False):
        if not counts_done:
            self.__initiate_print_count()
        n_pair = 0
        _1st_name = "andy"
        title = "COUNTING PAIRS"
        print("\n\n\n\n" + "#" * 33)
        print(f"#{title:^31}#")
        print("#" * 33)
        for pair, counts in sorted(
            self.pair_count.items(), key=lambda item: item[0]):
            if pair.split()[0] != _1st_name:
                print("# " + 29 * "-" + " #")
                _1st_name = pair.split()[0]
            n_pair += 1
            print(f"#{pair:^22}: {counts:^7}#")
        print("# " + 29 * "-" + " #")
        print("#" * 33)
        n_triple = 0
        _1st_name = "andy"
        title = "COUNTING TRIPLES"
        print("\n\n" + "#" * 41)
        print(f"#{title:^39}#")
        print("#" * 41)
        for team, counts in sorted(
            self.triple_count.items(), key=lambda item: item[0]):
            if team.split()[0] != _1st_name:
                print("# " + 37 * "-" + " #")
                _1st_name = team.split()[0]
            n_triple += 1
            print(f"#{team:^31}:{counts:^7}#")
        print("# " + 37 * "-" + " #")
        print(41 * "#")
        title = "NUMBER OF POSSIBLE"
        title2 = "FACE-OFFS"
        print("\n\n" + "#" * 29)
        print(f"#{title:^27}#")
        print(f"#{title2:^27}#")
        print("#" * 29)
        print("# " + 25 * "-" + " #")
        n_pair = f"{n_pair = }"; n_triple = f"{n_triple = }"
        print(f"#{n_pair:^27}#")
        print(f"#{n_triple:^27}#")
        print("# " + 25 * "-" + " #")
        print(29 * "#")
    
    # ------------------------------------------------------------------

    def __initiate_print_count(self):
        count_semis = True
        filenames = os.listdir(self.path_pair_counts)
        serie_now = self.serie.replace("/", "_")
        for ff in filenames:
            if serie_now in ff:
                self.__confirm_previous_series_counted(serie_now)
                self.__get_this_series_counts(serie_now)
                count_semis = False
        if count_semis:
            self.__get_counts_from_semis()
    
    # ------------------------------------------------------------------

    def __get_this_series_counts(self, serie_now):
        filename = self.path_pair_counts + f"pickled_counts_{serie_now}"
        pickled_counts = open(filename, "rb")
        all_counts = pickle.load(pickled_counts)
        self.pair_count = all_counts["pair"]
        self.triple_count = all_counts["triple"]
        pickled_counts.close()
    
    # ------------------------------------------------------------------

    def __get_counts_from_semis(self):
        self.__get_serie()
        for runde in self.rounds:
            self._semier = self.rounds[runde]
            self.__count_pairs_append()
    
    # ------------------------------------------------------------------

    def __get_serie(self):
        serie_txt = self.serie.replace("/", "_")
        pickled_semis = open(self.path_series + f"pickled_serie_{serie_txt}"\
                             + "_final", "rb")
        self.rounds = pickle.load(pickled_semis)
        pickled_semis.close()
    
    # ------------------------------------------------------------------

    def save_counts(self):
        filenames = os.listdir(self.path_pair_counts)
        serie_now = self.serie.replace("/", "_")
        self.__confirm_previous_series_counted(serie_now)
        for ff in filenames:
            if serie_now in ff:
                print("\nCounters for this series are already generated!")
                print(f"{self.serie = }\n")
                sys.exit()
        self.__get_previous_series_counts(serie_now)
        self.__get_counts_from_semis()
        serie_now = self.serie.replace("/", "_")
        filename = self.path_pair_counts + f"pickled_counts_{serie_now}"
        all_counts = {}
        all_counts["pair"] = self.pair_count
        all_counts["triple"] = self.triple_count
        pickle_semis = open(filename, "wb")
        pickle.dump(all_counts, pickle_semis)
        pickle_semis.close()
    
    # ------------------------------------------------------------------

    def write_counts_for_ode(self):
        serie_now = self.serie.replace("/", "_")
        self.__get_this_series_counts(serie_now)
        counts_txt = open(
            self.path_pair_counts + f"counts_{serie_now}_for_ode.txt", "w"
            )
        counts_txt.close()
        counts_txt = open(
            self.path_pair_counts + f"counts_{serie_now}_for_ode.txt", "a"
            )
        big_title = f"TOTAL NUMBER OF FACEOFFS (SEASON {self.serie})"
        counts_txt.write("#" * 77 + "\n")
        counts_txt.write("#" + " " * 75 + "#\n")
        counts_txt.write(f"#{big_title:^75}#\n")
        counts_txt.write("#" + " " * 75 + "#\n")
        counts_txt.write("#" * 77 + "\n\n")
        title_triple = "NUMBER OF MEETINGS"
        title_triple2 = "(TRIPLES)"
        counts_txt.write(" " * 36 + "#" * 41 + "\n")
        counts_txt.write(" " * 36 + f"#{title_triple:^39}#\n")
        counts_txt.write(" " * 36 + f"#{title_triple2:^39}#\n")
        counts_txt.write(" " * 36 + "#" * 41 + "\n")
        counts_txt.write(" " * 36 + "# " + 37 * "-" + " #\n")
        n_pair = 0
        n_triple = 0
        _1st_name_triple = "Andy"
        _1st_name_pair = "Andy"
        pairs = {}
        i = 0
        for pair, counts in sorted(
            self.pair_count.items(), key=lambda item: item[0]):
            pairs[i] = pair
            n_pair += 1
            i += 1
        for team, counts in sorted(
            self.triple_count.items(), key=lambda item: item[0]):
            n_triple += 1
        n_pair = f"{n_pair = }"; n_triple = f"{n_triple = }"
        n_meets = [n_pair, n_triple]
        i = 0
        i_pair = 0
        pair_start = 13
        pair_stop = pair_start + 48
        pair_params = [i_pair, pair_start, pair_stop, _1st_name_pair]
        i_n_meet = 0
        n_meet_start = pair_stop + 5
        n_meet_stop = n_meet_start + 9
        n_meet_params = [i_n_meet, n_meet_start, n_meet_stop]
        for team, counts in sorted(
            self.triple_count.items(), key=lambda item: item[0]):
            while team.split()[0] != _1st_name_triple:
                if i < pair_start:
                    line1 = " " * 36
                else:
                    line1 = self.__line1(pairs, n_meets, i, pair_params,
                                        n_meet_params)
                    if i == (n_meet_stop - 1):
                        n_meet_params[-1] -= 1
                line2 = "# " + 37 * "-" + " #"
                counts_txt.write(f"{line1 + line2}\n")
                _1st_name_triple = team.split()[0]
            if i < pair_start:
                line1 = " " * 36
            else:
                line1 = self.__line1(pairs, n_meets, i, pair_params,
                                     n_meet_params)
            line2 = f"#{team:^31}:{counts:^7}#"
            counts_txt.write(f"{line1 + line2}\n")
            i += 1
        counts_txt.write(" " * 36 + "# " + 37 * "-" + " #\n")
        counts_txt.write(" " * 36 + 41 * "#" + "\n")
    
    # ------------------------------------------------------------------

    def write_counts_for_me(self):
        
        
        n_pair = 0
        n_triple = 0
        big_title = "TOTAL NUMBER OF FACEOFFS"
        _1st_name_triple = "Andy"
        title_triple = "NUMBER OF MEETINGS"
        title_triple2 = "(TRIPLES)"
        _1st_name_pair = "Andy"
        print("#" * 77)
        print("#" + " " * 75 + "#")
        print(f"#{big_title:^75}#")
        print("#" + " " * 75 + "#")
        print("#" * 77 + "\n")
        print(" " * 36 + "#" * 41)
        print(" " * 36 + f"#{title_triple:^39}#")
        print(" " * 36 + f"#{title_triple2:^39}#")
        print(" " * 36 + "#" * 41)
        print(" " * 36 + "# " + 37 * "-" + " #")
        pairs = {}
        i = 0
        for pair, counts in sorted(
            self.pair_count.items(), key=lambda item: item[0]):
            pairs[i] = pair
            n_pair += 1
            i += 1
        for team, counts in sorted(
            self.triple_count.items(), key=lambda item: item[0]):
            n_triple += 1
        n_pair = f"{n_pair = }"; n_triple = f"{n_triple = }"
        n_meets = [n_pair, n_triple]
        i = 0
        i_pair = 0
        pair_start = 13
        pair_stop = pair_start + 48
        pair_params = [i_pair, pair_start, pair_stop, _1st_name_pair]
        i_n_meet = 0
        n_meet_start = pair_stop + 5
        n_meet_stop = n_meet_start + 9
        n_meet_params = [i_n_meet, n_meet_start, n_meet_stop]
        for team, counts in sorted(
            self.triple_count.items(), key=lambda item: item[0]):
            while team.split()[0] != _1st_name_triple:
                if i < pair_start:
                    line1 = " " * 36
                else:
                    line1 = self.__line1(pairs, n_meets, i, pair_params,
                                        n_meet_params)
                    if i == (n_meet_stop - 1):
                        n_meet_params[-1] -= 1
                line2 = "# " + 37 * "-" + " #"
                print(line1 + line2)
                _1st_name_triple = team.split()[0]
            if i < pair_start:
                line1 = " " * 36
            else:
                line1 = self.__line1(pairs, n_meets, i, pair_params,
                                     n_meet_params)
            line2 = f"#{team:^31}:{counts:^7}#"
            print(line1 + line2)
            i += 1
        print(" " * 36 + "# " + 37 * "-" + " #")
        print(" " * 36 + 41 * "#")
    
    # ------------------------------------------------------------------

    def __line1(self, pairs, n_meets, i, pair_params, n_meet_params):
        i_pair, pair_start, pair_stop, _1st_name_pair = pair_params
        i_n_meet, n_meet_start, n_meet_stop = n_meet_params
        init_pair, init_n_meet = self.__init_titles()
        if pair_start <= i < pair_stop:
            if i_pair < 36:
                pair = pairs[i_pair]
            else:
                pair = pairs[len(pairs) - 1]
            if i < (pair_start + 5):
                line1 = init_pair[i - pair_start]
            elif pair.split()[0] != _1st_name_pair:
                line1 = "# " + 29 * "-" + " #   "
                pair_params[-1] = pair.split()[0]
            elif i_pair < 36:
                pair = pairs[i_pair]
                counts_p = self.pair_count[pair]
                line1 = f"#{pair:^22}: {counts_p:^7}#   "
                pair_params[0] += 1
            else:
                line1 = init_pair[-(i - pair_stop + 3)]
        elif pair_stop <= i < n_meet_start:
            line1 = " " * 36
        elif n_meet_start <= i < n_meet_stop:
            if i < (n_meet_start + 5):
                line1 = init_n_meet[i - n_meet_start]
            elif i_n_meet < 2:
                n_meet = n_meets[i_n_meet]
                line1 = f"  #{n_meet:^27}#     "
                n_meet_params[0] += 1
            else:
                line1 = init_n_meet[-(i - n_meet_stop + 3)]
        else:
            line1 = " " * 36
        return line1
    
    # ------------------------------------------------------------------

    def __init_titles(self):
        title_pair = "NUMBER OF MEETINGS"
        title_pair2 = "(PAIRS)"
        title_n_meet = "NUMBER OF POSSIBLE"
        title_n_meet2 = "PAIRS VS TRIPLES"
        init_title_pair = ["#" * 33 + "   ",
                           f"#{title_pair:^31}#   ",
                           f"#{title_pair2:^31}#   ",
                           "#" * 33 + "   ",
                           "# " + 29 * "-" + " #   "]
        init_title_n_meet = ["  " + "#" * 29 + "     ",
                             f"  #{title_n_meet:^27}#     ",
                             f"  #{title_n_meet2:^27}#     ",
                             "  " + "#" * 29 + "     ",
                             "  # " + 25 * "-" + " #     "]
        return init_title_pair, init_title_n_meet
    
    # ------------------------------------------------------------------

    def dash_print_semifinals(self):
        """
        Printing semi-finals with dashes as frame
        """
        self.__get_serie()
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
        print("\n\n\n")
    
    # ------------------------------------------------------------------

    def dash_write_semifinals(self):
        """
        Writing semi-finals to .txt-file with dashes as frame
        """
        self.__get_serie()
        serie_txt = self.serie.replace("/", "_")
        semis_txt = open(self.path_series + f"serie_{serie_txt}.txt", "w")
        semis_txt.close()
        semis_txt = open(self.path_series + f"serie_{serie_txt}.txt", "a")
        under, dash, hash, pipes = ("_", "-", "#", "|" + 37 * " " + "|")
        title = f"SEMI-FINALS {self.serie}"
        title = f"#{title:^37}#"
        semis_txt.write(f"{39 * hash:^72}\n")
        semis_txt.write(f"{title:^72}\n")
        semis_txt.write(f"{39 * hash:^72}\n")
        for runde in self.rounds:
            title = f"Round {runde}"
            title = f"|{title:^14}|"
            semis_txt.write(f"{16 * under:^72}\n")
            semis_txt.write(f"{title:^72}\n")
            semis_txt.write(f"{39 * dash:^72}\n")
            semis_txt.write(f"{pipes:^72}\n")
            tmp = self.rounds[runde]
            for i in range(len(tmp)):
                line = f"{tmp[i][0]}, {tmp[i][1]}, {tmp[i][2]}"
                line = f"|{line:^37}|"
                semis_txt.write(f"{line:^72}\n")
            semis_txt.write(f"{pipes:^72}\n")
            semis_txt.write(f"{39 * dash:^72}\n")
        semis_txt.close()
    
    # ------------------------------------------------------------------






def main():
    boolt, boolf = (True, False)
    # serie 1 = 22/23
    series = {0: "22/23", 1: "23/24"}
    serie = series[0]

    # !!!!!!!!!!!!!!!!!
    # ARE YOU DESPERATE? (True/False)
    # !!!!!!!!!!!!!!!!!

    ode = Dart(serie, verbose=boolt, desperate=boolf)
    functions = {0: "ode.generate_semi_finals(1)",
                 1: "ode.dash_write_semifinals()",
                 2: "ode.scoring()",
                 3: "ode.dash_print_semifinals()",
                 4: "ode.print_counts()",
                 5: "ode.save_counts()",
                 6: "ode.write_counts_for_ode()",
                 7: "ode.write_counts_for_me()"}
    func = functions[6]
    exec(func)

if __name__ == "__main__":
    main()