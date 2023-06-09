def init_dictionary():
    element_dictionary: dict[str, []] = {
        "resistor10Om": [(11, 4.5), "resistor10Om", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "resistor1kOm": [(11, 4.5), "resistor1kOm", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "resistor100Om": [(11, 4.5), "resistor100Om", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "resistor1Om": [(11, 4), "resistor1Om", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "capacitor10mkF": [(4.5, 3.2), "capacitor10mkF", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "capacitor100mkF": [(3.5, 2.8), "capacitor100mkF", [[], [], ["up", [2], [], 1], ["down", [2], [], 1]]],
        "capacitor1mkF": [(2, 1.25), "capacitor1mkF", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "inductance220mkG": [(12, 7.5), "inductance220mkG", [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]],
        "inductance10mkG": [(3.2, 1.8), "inductance10mkG", [[], [], ["up", [1], [], 1], ["down", [1], [], 1]]],
        "K176TM2": [(19.5, 6.6), "K176TM2", [["left", [1, 2, 3, 4, 5, 6, 7], [], 2.5],
                                             ["right", [1, 2, 3, 4, 5, 6, 7], [], 2.5],
                                             [], []]],
        "TPS51200DRCR": [(3, 3), "TPS51200DRCR", [["left", [1, 2, 3, 4, 5], [], 0.5],
                                                  ["right", [1, 2, 3, 4, 5], [], 0.5], [], []]],
        "CS48505S": [(4.9, 3.9), "CS48505S",
                     [["left", [1, 2, 3, 4], [], 1.27], ["right", [1, 2, 3, 4], [], 1.27], [], []]],
        "ADM3070EARZ": [(8.5, 6), "ADM3070EARZ", [["left", [1, 2, 3, 4, 5, 6, 7], [], 1.27],
                                                  ["right", [1, 2, 3, 4, 5, 6, 7], [], 1.27], [], []]],
        "AD790JNZ": [(9.4, 6.2), "AD790JNZ",
                     [["left", [1, 2, 3, 4], [], 2.54], ["right", [1, 2, 3, 4], [], 2.54], [], []]],
        "CD74HC123E": [(19.45, 6.6), "CD74HC123E", [["left", [1, 2, 3, 4, 5, 6, 7, 8], [], 2.54],
                                                    ["right", [1, 2, 3, 4, 5, 6, 7, 8], [], 2.54], [], []]],
        "23LC1024-I/SN": [(4.9, 3.9), "23LC1024-I/SN", [["left", [1, 2, 3, 4], [], 1.27]]],
        "ADUC812BSZ": [(16, 16), "ADUC812BSZ", [["left", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9],
                                                ["right", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9],
                                                ["up", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9],
                                                ["down", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9]]],
        "AD420ARZ-32-REEL": [(15.2, 7.6), "AD420ARZ-32-REEL",
                             [["left", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [], 1.27],
                              ["right", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [], 1.27], [], []]],
        "ground": [(1, 1), "ground", [[], [], ["up", [1], [], 1], []]]}
    return element_dictionary


def init_configuration_dict():
    el_dict = init_dictionary()
    configs: dict[str, []] = {"config1": [[el_dict["K176TM2"], 20, 20, "", [[("A1", "in"), ("A2", "in"), ("A3", ""),
                                                                             ("A4", ""), ("A5", ""), ("A6", ""),
                                                                             ("A7", "")],
                                                                            [("A8", ""), ("A9", ""), ("A10", "out"),
                                                                             ("A11", ""), ("A12", ""), ("A13", ""),
                                                                             ("A14", "")], [], []]],
                                          [el_dict["ground"], 40, 40, "", [[], [], [("A1", "out")], []]],
                                          [el_dict["K176TM2"], 10, 40, "", [[("A1", "in"), ("A2", "out"), ("A3", ""),
                                                                             ("A4", ""), ("A5", ""), ("A6", ""),
                                                                             ("A7", "")],
                                                                            [("A8", ""), ("A9", ""), ("A10", "in"),
                                                                             ("A11", ""), ("A12", ""), ("A13", ""),
                                                                             ("A14", "")], [], []]],
                                          [el_dict["ADUC812BSZ"], 50, 50, "", [[("A1", "in"), ("A2", "out"), ("A3", ""),
                                                                                ("A4", ""), ("A5", ""), ("A6", ""),
                                                                                ("A7", ""), ("A8", ""), ("A9", ""),
                                                                                ("A10", "in"),
                                                                                ("A11", ""), ("A12", "in"), ("A13", ""),
                                                                                ("A14", "")], [], [], []]],
                                          [el_dict["ground"], 60, 30, "", [[], [], [("A12", "out")], []]]],
                              "config2": [[el_dict["K176TM2"], 10, 40, "", [[], [("A1", ""), ("A2", ""), ("A3", ""),
                                                                                 ("A4", ""), ("A5", "in"), ("A6", ""),
                                                                                 ("A7", "in")], [], []]],
                                          [el_dict["ADUC812BSZ"], 30, 25, "",
                                           [[("A1", "out"), ("A2", ""), ("A3", ""),
                                             ("A4", ""), ("A5", "out"), ("A6", ""), ("A7", "out"),
                                             ("A8", ""), ("A9", ""), ("A10", ""),
                                             ("A11", ""), ("A12", ""), ("A13", "")],
                                            [("A14", ""), ("A15", ""), ("A16", ""),
                                             ("A17", ""), ("A18", "out"), ("A19", ""), ("A20", ""),
                                             ("A21", ""), ("A22", ""), ("A23", ""),
                                             ("A24", ""), ("A25", ""), ("A26", "")],
                                            [("A27", ""), ("A28", "in"), ("A29", ""),
                                             ("A30", ""), ("A31", ""), ("A32", ""), ("A33", ""),
                                             ("A34", ""), ("A35", ""), ("A36", ""),
                                             ("A37", ""), ("A38", "out"), ("A39", "")],
                                            [("A40", ""), ("A41", "in"), ("A42", ""),
                                             ("A43", ""), ("A44", "out"), ("A45", ""), ("A46", ""),
                                             ("A47", ""), ("A48", ""), ("A49", ""),
                                             ("A50", ""), ("A51", "in"), ("A52", "")]]],
                                          [el_dict["K176TM2"], 30, 40, "left",
                                           [[], [("A1", ""), ("A41", "out"), ("A44", "in"),
                                                 ("A4", ""), ("A51", "out"), ("A6", ""),
                                                 ("A7", "")], [], []]],
                                          [el_dict["ground"], 5, 5, "", [[], [], [("A1", "in")], []]],
                                          [el_dict["ground"], 40, 30, "", [[], [], [("A18", "in")], []]],
                                          [el_dict["resistor1Om"], 30, 5, "left",
                                           [[], [], [("A28", "out")], [("A38", "in")]]]
                                          ], "config3": [
            [el_dict["ground"], 0, 5, "right", [[], [], [("A1", "in")], [], []]],
            [el_dict["ground"], 5, 0, "left", [[], [], [("A1", "out")], [], []]],
            [el_dict["ground"], 5, 5, "right", [[], [], [("A2", "in")], [], []]],
            [el_dict["ground"], 2, 2, "left", [[], [], [("A2", "out")], [], []]],
            [el_dict["ground"], 1, 1, "right", [[], [], [("A3", "in")], [], []]],
            [el_dict["ground"], 2, 1, "left", [[], [], [("A3", "out")], [], []]],
            [el_dict["ground"], 2, 3, "right", [[], [], [("A4", "in")], [], []]],
            [el_dict["ground"], 1, 4, "left", [[], [], [("A4", "out")], [], []]]],
                              "config4": [
                                  [el_dict["ground"], 0, 5, "right", [[], [], [("A1", "in")], [], []]],
                                  [el_dict["ground"], 5, 0, "left", [[], [], [("A1", "out")], [], []]],
                                  [el_dict["ground"], 5, 5, "right", [[], [], [("A2", "in")], [], []]],
                                  [el_dict["ground"], 2, 2, "left", [[], [], [("A2", "out")], [], []]]]

                              }
    return configs