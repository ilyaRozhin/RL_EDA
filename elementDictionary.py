# Подумать насчет поворота элементов

spec_pin_mass = [["left", [], []], ["right", [], []], ["up", [], []], ["down", [], []]]

ElementDictionary: dict[str, BoardElement] = {"resistor10Om": BoardElement, "resistor1kOm": BoardElement,
                                              "resistor100Om": BoardElement, "resistor1Om": BoardElement,
                                              "capacitor10mkF": BoardElement, "capacitor100mkF": BoardElement,
                                              "capacitor1mkF": BoardElement, "inductance220mkG": BoardElement,
                                              "inductance10mkG": BoardElement, "K176TM2": BoardElement,
                                              "TPS51200DRCR": BoardElement, "CS48505S":  BoardElement,
                                              "ADM3070EARZ": BoardElement, "AD790JNZ": BoardElement,
                                              "CD74HC123E": BoardElement, "23LC1024-I/SN": BoardElement,
                                              "ADUC812BSZ": BoardElement, "AD420ARZ-32-REEL": BoardElement}
buf = spec_pin_mass
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["resistor1Om"] = BoardElement(0, 0, 11, 4, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["resistor10Om"] = BoardElement(0, 0, 11, 4.5, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["resistor100Om"] = BoardElement(0, 0, 11, 4.5, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["resistor1kOm"] = BoardElement(0, 0, 11, 4.5, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["capacitor10mkF"] = BoardElement(0, 0, 4.5, 3.2, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["capacitor1mkF"] = BoardElement(0, 0, 2, 1.25, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["capacitor100mkF"] = BoardElement(0, 0, 3.5, 2.8, 1).append_pins(spec_pin_mass)

spec_pin_mass = buf
spec_pin_mass[2][1] = [1]
spec_pin_mass[3][1] = [1]
ElementDictionary["capacitor10mkF"] = BoardElement(0, 0, 4.5, 3.2, 1).append_pins(spec_pin_mass)

