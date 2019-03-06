#!/usr/bin/python3

import moiety_modeling
import jsonpickle

dataset1 = moiety_modeling.Dataset("1_24h",
                                      {'UDP_GlcNAC': [{'labelingIsotopes': '13C0', 'height': 0.00697626, 'heightSE': 0},
                                                      {'labelingIsotopes': '13C1', 'height': 0, 'heightSE': 0},
                                                      {'labelingIsotopes': '13C2', 'height': 0.0008426934,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C3', 'height': 0.0007070956,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C4', 'height': 0.0006206594,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C5', 'height': 0.068147345,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C6', 'height': 0.0499393097,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C7', 'height': 0.023993641,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C8', 'height': 0.062901247,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C9', 'height': 0.0056603032,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C10', 'height': 0.0281210238,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C11', 'height': 0.2482899264,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C12', 'height': 0.0613088541,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C13', 'height': 0.3325253653,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C14', 'height': 0.0499904271,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C15', 'height': 0.0537153908,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C16', 'height': 0.0062604583,
                                                       'heightSE': 0},
                                                      {'labelingIsotopes': '13C17', 'height': 0, 'heightSE': 0}]})

dataset2 = moiety_modeling.Dataset("1_36h", {
    'UDP_GlcNAC': [{'labelingIsotopes': '13C0', 'height': 0.0009166044, 'heightSE': 0},
                   {'labelingIsotopes': '13C1', 'height': 0, 'heightSE': 0},
                   {'labelingIsotopes': '13C2', 'height': 0, 'heightSE': 0},
                   {'labelingIsotopes': '13C3', 'height': 4.62586843804159E-06, 'heightSE': 0},
                   {'labelingIsotopes': '13C4', 'height': 0.0003291166, 'heightSE': 0},
                   {'labelingIsotopes': '13C5', 'height': 0.0461930963, 'heightSE': 0},
                   {'labelingIsotopes': '13C6', 'height': 0.0411700819, 'heightSE': 0},
                   {'labelingIsotopes': '13C7', 'height': 0.0173512837, 'heightSE': 0},
                   {'labelingIsotopes': '13C8', 'height': 0.0516141159, 'heightSE': 0},
                   {'labelingIsotopes': '13C9', 'height': 0.0027135558, 'heightSE': 0},
                   {'labelingIsotopes': '13C10', 'height': 0.0224157713, 'heightSE': 0},
                   {'labelingIsotopes': '13C11', 'height': 0.2514380699, 'heightSE': 0},
                   {'labelingIsotopes': '13C12', 'height': 0.0718100061, 'heightSE': 0},
                   {'labelingIsotopes': '13C13', 'height': 0.3662556844, 'heightSE': 0},
                   {'labelingIsotopes': '13C14', 'height': 0.0597315432, 'heightSE': 0},
                   {'labelingIsotopes': '13C15', 'height': 0.0579801179, 'heightSE': 0},
                   {'labelingIsotopes': '13C16', 'height': 0.0100763266, 'heightSE': 0},
                   {'labelingIsotopes': '13C17', 'height': 0, 'heightSE': 0}]})


dataset3 = moiety_modeling.Dataset("2_24h", {'UDP_GlcNAC': [{'labelingIsotopes': '13C0', 'height': 0.0054112001, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C1', 'height': 0, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C2', 'height': 0.0002443601, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C3', 'height': 0, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C4', 'height': 0.0006771256, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C5', 'height': 0.0601364562, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C6', 'height': 0.0505878726, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C7', 'height': 0.0257101541, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C8', 'height': 0.0558144077, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C9', 'height': 0.0078118293, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C10', 'height':  0.0238954121, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C11', 'height':  0.2451402014, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C12', 'height':  0.0650931207, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C13', 'height':  0.3471455508, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C14', 'height':  0.0524199207, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C15', 'height': 0.0546107206, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C16', 'height':  0.0053016678, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C17', 'height': 0, 'heightSE': 0}]})


dataset4 = moiety_modeling.Dataset("2_36h", {'UDP_GlcNAC': [{'labelingIsotopes': '13C0', 'height': 0.0013563833, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C1', 'height': 0, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C2', 'height': 0.000470185, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C3', 'height': 0.0002145004, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C4', 'height': 0.0008907347, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C5', 'height': 0.0470947611, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C6', 'height': 0.0371916408, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C7', 'height': 0.0219394801, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C8', 'height':  0.0486243453, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C9', 'height': 0.0056235016, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C10', 'height':  0.0243139349, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C11', 'height':  0.2437263469, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C12', 'height':  0.0664551468, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C13', 'height':  0.3776013587, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C14', 'height': 0.0617711234, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C15', 'height': 0.0555852048, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C16', 'height':  0.0071413523, 'heightSE': 0},
                                                        {'labelingIsotopes': '13C17', 'height': 0, 'heightSE': 0}]})



dataset = { 'datasets' : [ dataset1, dataset2, dataset3, dataset4 ]}
jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
with open('maims_combinedData_24_36.json', 'w') as outFile:
    outFile.write(jsonpickle.encode(dataset))
