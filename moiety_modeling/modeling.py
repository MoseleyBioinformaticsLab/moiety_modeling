#!/usr/bin/python3

"""
moiety_modeling.modeling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the :class:`~moiety_modeling.modeling.Dataset` class to organize a single mass spectroscopy
profile dataset in the form of an :py:class:`~collections.UserDict`, and the :class:`~moiety_modeling.modeling.OptimizationManager`
class to manage the optimization process of moiety modeling.

The optimization results are stored in the JSON file. A txt file containing all the paths to the generated ``JSON`` files is
created to facilitate further model analysis.
"""

import sys
import SAGA_optimize
import operator
import functools
import jsonpickle
import collections
import multiprocessing
import os
import scipy
import scipy.optimize
import abc
import random
import math
import logging
import shutil

__all__ = ['Dataset', 'OptimizationManager']

class Dataset(collections.UserDict):

    """Dataset class that stores a single mass spectroscopy profile in the form of :py:class:`~collections.UserDict`."""

    def __init__(self, datasetName, *args, **kwargs):
        """Dataset initializer.

        :param str datasetName: the name of the dataset.
        """
        self.datasetName = datasetName
        super().__init__(*args, **kwargs)


class ModelOptimization(abc.ABC):

    """
    The abstract class of model optimization.
    """

    def __init__(self, model, datasets, path, methodParameters, optimizationSetting, energyFunction):

        """

        :param model: the moiety model.
        :param datasets: list of datasets of metabolite isotopologues.
        :param path:
        :param optimizationSetting:
        """

        self.model = model
        self.datasets = datasets
        self.path = path
        self.methodParameters = methodParameters
        self.optimizationSetting = optimizationSetting
        self.energyFunction = energyFunction
        self.functionCollection = {'absDifference': self.absDifferenceEnergyFunction, 'logDifference': self.logDifferenceEnergyFunction, 'proportionalDifference': self.proportionalEnergyFunction}
        self.activeEnergyFunction = self.functionCollection[self.energyFunction]
        self.bestGuesses = []
        self.elements = self._createElements()

    def _createElements(self):

        """
        To create parameters for optimization.
        :return: the list of parameters.
        """

        elements = []
        for dataset in self.datasets:
            for moiety in self.model.orderedMoieties:
                elements += [ '{0}.{1}'.format(dataset.datasetName, element) for element in self.model.properties[moiety.name]['elementNames'] ]
        return elements

    def energyCalculation(self, vector):

        """
        To calculate the energy in the model.
        :param vector: the list of parameter value.
        :return: the energy.
        """

        energy = 0
        for i in range(len(self.datasets)):
            subVector = [ vector[i] for i in range(i* self.model.parameterNum, (i+1) * self.model.parameterNum) ]
            energy += self.activeEnergyFunction(self.model.calculateMoietyState(subVector), self.datasets[i])
        return energy

    def absDifferenceEnergyFunction(self, moietyStateValue, dataset):

        """To calculate the energy of model. The absolute value between the observed and the calculated isotopologues.
            energy = sum(|I<cal> - I<obs>|)

        :param moietyStateValue: the list of value of the moietyStates.
        :param dataset: the dataset object.
        :return: the energy of the model.
        """

        energy = 0
        for molecule in self.model.molecules:
            if len(dataset[molecule.name]) != len(molecule.allStates):
                sys.exit("The isotologue data of {0} is not enough.".format(molecule.name))
            calculated = collections.defaultdict(lambda: 0)
            for isotopologue in molecule.standardStates:
                calculated[isotopologue] = sum(functools.reduce(operator.mul, [moietyStateValue[i] for i in isotopomer]) for isotopomer in molecule.standardStates[isotopologue])
            energy += sum([abs(calculated[isotopologue['labelingIsotopes']] - isotopologue['height']) for isotopologue in dataset[molecule.name]])
        return energy

    def logDifferenceEnergyFunction(self, moietyStateValue, dataset):

        """To calculate the energy of model. The difference between the log of observed and the calculated isotopologues.
            energy = sum(|log(I<cal>) - log(I<obs>)|)

        :param moietyStateValue: the list of value of the moietyStates.
        :param dataset: the dataset object.
        :return: the energy of the model.
        """

        energy = 0
        for molecule in self.model.molecules:
            if len(dataset[molecule.name]) != len(molecule.allStates):
                sys.exit("The isotopologue data of {0} is not enough.".format(molecule.name))
            calculated = collections.defaultdict(lambda: 0)
            for isotopologue in molecule.standardStates:
                calculated[isotopologue] = sum(functools.reduce(operator.mul, [moietyStateValue[i] for i in isotopomer]) for isotopomer in molecule.standardStates[isotopologue])
            leastIsotopologue = min([isotopologue['height'] for isotopologue in dataset[molecule.name] if isotopologue['height'] > 0]) / 2
            for isotopologue in dataset[molecule.name]:
                if calculated[isotopologue['labelingIsotopes']] != 0 and isotopologue['height'] == 0:
                    energy += abs(math.log(calculated[isotopologue['labelingIsotopes']]) - math.log(leastIsotopologue))
                elif calculated[isotopologue['labelingIsotopes']] == 0 and isotopologue['height'] != 0:
                    energy += abs(math.log(leastIsotopologue) - math.log(isotopologue['height']))
                elif calculated[isotopologue['labelingIsotopes']] != 0 and isotopologue['height'] != 0:
                    energy += abs(math.log(calculated[isotopologue['labelingIsotopes']]) - math.log(isotopologue['height']))
        return energy

    def proportionalEnergyFunction(self, moietyStateValue, dataset):

        """To calculate the energy of the  model. The relative difference between calculated and observed isotopologues.
            energy = sum(|I<cal> - I<obs>)/I<obs>|)

        :param moietyStateValue: the list of value of the moietyStates.
        :param dataset: the dataset object.
        :return:the energy of the model.
        """

        energy = 0
        for molecule in self.model.molecules:
            if len(dataset[molecule.name]) != len(molecule.allStates):
                sys.exit("The data of {0} is not enough.".format(molecule.name))
            calculated = collections.defaultdict(lambda: 0)
            for isotopologue in molecule.standardStates:
                calculated[isotopologue] = sum(functools.reduce(operator.mul, [moietyStateValue[i] for i in isotopomer]) for isotopomer in molecule.standardStates[isotopologue])
            leastIsotopologue = min([isotopologue['height'] for isotopologue in dataset[molecule.name] if isotopologue['height'] > 0]) / 2
            for isotopologue in dataset[molecule.name]:
                if isotopologue['height'] != 0:
                    energy += abs((calculated[isotopologue['labelingIsotopes']] - isotopologue['height']) / isotopologue['height'])
                else:
                    energy += abs((calculated[isotopologue['labelingIsotopes']] - leastIsotopologue) / leastIsotopologue)
        return energy

    def optimizationScripts(self):

        """
        To save the optimization scripts of the optimization for check.
        :return:
        """

        outputFile = open('{0}{1}_{2}_optimization_scripts.txt'.format(self.path, self.model.name, self.optimizationSetting), 'w')
        outputFile.write(self.model.name+'\n')
        for moiety in self.model.moieties:
            outputFile.write(str(moiety)+'\n')
        for relationship in self.model.relationships:
            outputFile.write(str(relationship)+'\n')
        for molecule in self.model.molecules:
            outputFile.write(str(molecule)+'\n')
        for dataset in self.datasets:
            outputFile.write("Dataset {0}\n".format(dataset.datasetName))
            for molecule in self.model.molecules:
                outputFile.write(" {0} data = {1}\n".format(molecule.name, dataset[molecule.name]))
        outputFile.write(str(self.model))
        string = "\n energy = 0\n"
        for molecule in self.model.molecules:
            string += " {0}_cal = {1}\n".format(molecule.name, {labelingIsotopes: 0 for labelingIsotopes in molecule.allStates})
            for isotopologue in molecule.allStates:
                string += " {0}_calc[{1}] = {2}\n".format(molecule.name, isotopologue, ' + '.join(['.'.join(isotopomer) for isotopomer in molecule.standardStates[isotopologue]]))
            string += "\n {0}Obeserved = data['{1}']\n".format(molecule.name, molecule.name)
            string += " for x in range(len({0}Observed)):\n".format(molecule.name)
            if self.energyFunction == 'absDifference':
                string += "     energy += abs({0}_calc[{0}Observed[x]['labelingIsotopes']] - {0}Observed[x]['height'])\n".format(molecule.name)
            elif self.energyFunction == 'logDifference':
                string += "     energy += abs(log({0}_calc[{0}Observed[x]['labelingIsotopes']) - log({0}Observed[x]['height']\n)".format(molecule.name)
            elif self.energyFunction == 'proportionalDifference':
                string += "     energy += abs(({0}_calc[{0}Observed[x]['labelingIsotopes']] - {0}Observed[x]['height']) / {0}Observed[x]['height'])\n".format(molecule.name)
        string += ' return energy'
        outputFile.write(string)
        outputFile.close()


class SAGAoptimization(ModelOptimization):

    """
    The class of SAGA optimization (for combined datasets) inherited from ModelOptimization class.
    """

    def __init__(self, model, datasets, path, methodParameters, optimizationSetting, energyFunction, noPrintBestResults, noPrintAllResults):

        """

        :param model: the model.
        :param datasets: list of datasets.
        :param path:
        :param noPrintAllResults:
        :param methodParameters:
        :param optimizationSetting:
        """

        super().__init__(model, datasets, path, methodParameters, optimizationSetting, energyFunction)
        self.noPrintBestResults = noPrintBestResults
        self.noPrintAllResults = noPrintAllResults

    def bestResultsFile(self, i):

        """
        Open the file to record the best results during the optimization process.
        :param i: the ith optimization.
        :param datasetName: the name of the dataset.
        :return: the file handler.
        """

        if self.noPrintBestResults:
            return None

        return open('{0}{1}_best/{1}_best_results_{2}_{3}.txt'.format(self.path, self.model.name, self.optimizationSetting, i), 'w')

    def allResultsFile(self, i):

        """
        Open the file to record the all optimization results.
        :param i: the ith optimization.
        :param datasetName: the name of the dataset.
        :return: file handler.
        """

        if self.noPrintAllResults:
            return None

        return open('{0}{1}_all/{1}_best_results_{2}_{3}.txt'.format(self.path, self.model.name, self.optimizationSetting, i), 'w')

    def optimizeSingle(self, i):

        """
        To perform one optimization.
        :param i: the ith optimization.
        :return:
        """

        saga = SAGA_optimize.SAGA(**self.methodParameters, bestResultsFile=self.bestResultsFile(i), allResultsFile=self.allResultsFile(i), energyCalculation=self.energyCalculation)
        for element in self.elements:
            saga.addElementDescriptions(SAGA_optimize.ElementDescription(name=element, low=0, high=1))
        optimizedPopulation = saga.optimize()
        if saga.allResultsFile:
            saga.allResultsFile.close()
        if saga.bestResultsFile:
            saga.bestResultsFile.close()
        return optimizedPopulation.bestGuess

    def creatSubdir(self):

        """
        To create subdirectories to store the optimization process.
        :return:
        """

        if not self.noPrintBestResults:
            os.makedirs(self.path+self.model.name+'_best')
        if not self.noPrintAllResults:
            os.makedirs(self.path + self.model.name + '_all')


class SAGAseparateOptimization(SAGAoptimization):

    """
    The class of SAGA optimization (for split datasets) inherited from the SAGAoptimization class.
    """

    def __init__(self, model, datasets, path, methodParameters, optimizationSetting, energyFunction, noPrintBestResults, noPrintAllResults):
        super().__init__(model, datasets, path, methodParameters, optimizationSetting, energyFunction, noPrintBestResults, noPrintAllResults)

    def optimizeSingle(self, i):

        """
        Perform one optimization.
        :param i: the ith optimization.
        :return: the best Guess of the optimization.
        """

        bestGuesses = []
        for dataset in self.datasets:
            optimization = SAGAoptimization(self.model, [dataset], self.path, self.methodParameters, self.optimizationSetting + '_' + dataset.datasetName, self.energyFunction, self.noPrintBestResults, self.noPrintAllResults)
            bestGuesses.append(optimization.optimizeSingle(i))
        combinedGuess = bestGuesses[0]
        for i in range(1, len(bestGuesses)):
            combinedGuess.elementDescriptions += bestGuesses[i].elementDescriptions
            combinedGuess.elements += bestGuesses[i].elements
            combinedGuess.energy += bestGuesses[i].energy
        return combinedGuess


class ScipyGuess:
    """
    To convert optimization solution to Guess format.
    """

    def __init__(self, elements, energy):
        """
        :param elements: a list of value to parameters.
        :param energy: the energy of this solution.
        """
        self.elements = elements
        self.energy = energy


class ScipyOptimization(ModelOptimization):

    """
    The class of Scipy optimization (for combined datasets) inherited from ModelOptimization class.
    """

    def __init__(self, model, datasets, path, methodParameters, optimizationSetting, energyFunction, method):

        """

        :param model: the moiety model.
        :param datasets: the list of datasets of metabolite isotopologues.
        :param method: the method in Scipy for optimization.
        :param path:
        :param optimizationSetting:
        """

        super().__init__(model, datasets, path, methodParameters, optimizationSetting, energyFunction)
        self.method = method

    def optimizeSingle(self, i):

        """
        To perform one optimization.
        :param i: the ith optimization.
        :return: the best Guess object of the optimization.
        """

        bounds = scipy.array([(0, 1) for _ in self.elements])
        fun = lambda vector: self.energyCalculation(vector)
        while True:
            initialGuess = scipy.array([random.random() for _ in self.elements])
            optimizeResult = scipy.optimize.minimize(fun, initialGuess, method=self.method, bounds=bounds, options=self.methodParameters)
            if optimizeResult.success:
                bestGuess = ScipyGuess(optimizeResult.x.tolist(), fun(optimizeResult.x.tolist()))
                break
            else:
                continue
        return bestGuess


class ScipySeparateOptimization(ScipyOptimization):

    """
    The class of Scipy optimization (for split datasets) inherited from ScipyOptimization class.
    """

    def __init__(self, model, datasets, path, methodParameters, energyFunction, optimizationSetting, method):
        super().__init__(model, datasets, path, methodParameters, energyFunction, optimizationSetting, method)

    def optimizeSingle(self, i):

        """
        To perform single optimization.
        :param i: the ith optimization.
        :return: the best Guess of the optimization.
        """

        bestGuesses = []
        for dataset in self.datasets:
            optimization = ScipyOptimization(self.model, [dataset], self.path, self.methodParameters, self.optimizationSetting + '_' + dataset.datasetName, self.energyFunction, self.method)
            bestGuesses.append(optimization.optimizeSingle(i))
        elements = []
        energy = 0
        for i in range(len(bestGuesses)):
            elements += bestGuesses[i].elements
            energy += bestGuesses[i].energy
        return ScipyGuess(elements, energy)


class OptimizationManager:

    """OptimizationManager class manage the optimization process based on the optimization settings."""

    def __init__(self, models, datasets, optimizations, path, split=True, multiprocess=True, force=True, times=100, energyFunction='logDifference', printOptimizationScript=True):
        """OptimizationManager initializer.

        :param list models: a list of :class:`~moiety_modeling.model.Moiety` instances.
        :param list datasets: a list of :class:`~moiety_modeling.modeling.Dataset` instances.
        :param dict optimizations: a list of optimization settings.
        :param str path: the path to store the optimization results.
        :param True split: to split the dataset or not.
        :param True multiprocess: to apply multiprocess or not.
        :param True force: to force optimization process or not.
        :param int times: the times of optimization for each moiety model.
        :param str energyFunction: the energy function used for optimization.
        :param True printOptimizationScript: to print out the optimization script or not.
        """

        self.models = models
        self.datasets = datasets
        self.optimizations = optimizations
        self.path = path
        self.split = split
        self.multiprocess = multiprocess
        self.force = force
        self.times = times
        self.energyFunction = energyFunction
        self.printOptimizationScript = printOptimizationScript

    def optimizeModels(self):
        """To optimize moiety models based on the optimization settings.

        :return: None
        :rtype: :py:obj:`None`
        """

        logger = self._initLogging()

        for optimizationMethod in self.optimizations:

            optimizationParameters = self.optimizations[optimizationMethod]

            if not os.path.exists(self.path + '/' + optimizationParameters['optimizationSetting']):
                os.mkdir(self.path + '/' + optimizationParameters['optimizationSetting'])
            path = self.path + '/' + optimizationParameters['optimizationSetting'] + '/'

            for model in self.models:

                datasets = []
                datasetName = ''

                for dataset in self.datasets:
                    # datasets can contain more molecules than model.

                    if set([molecule.name for molecule in model.molecules]).issubset(set(dataset.keys())):
                        datasetName += dataset.datasetName + " "
                        datasets.append(dataset)

                if datasets:
                    logger.info("Performing {0} optimization on {1} with {2}dataset".format(optimizationParameters['optimizationSetting'], model.name, datasetName))

                    if optimizationMethod == 'SAGA':
                        if self.split:
                            optimization = SAGAseparateOptimization(model, datasets, path,  optimizationParameters['methodParameters'], optimizationParameters['optimizationSetting'], self.energyFunction, optimizationParameters['noPrintBestResults'], optimizationParameters['noPrintAllResults'])
                        else:
                            optimization = SAGAoptimization(model, datasets, path, optimizationParameters['methodParameters'], optimizationParameters['optimizationSetting'], self.energyFunction, optimizationParameters['noPrintBestResults'], optimizationParameters['noPrintAllResults'])
                        optimization.creatSubdir()
                    elif optimizationMethod in ['L-BFGS-B', 'TNC', 'SLSQP']:
                        if self.split:
                            optimization = ScipySeparateOptimization(model, datasets, path, optimizationParameters['methodParameters'], optimizationParameters['optimizationSetting'], self.energyFunction, optimizationMethod)
                        else:
                            optimization = ScipyOptimization(model, datasets, path, optimizationParameters['methodParameters'], optimizationParameters['optimizationSetting'], self.energyFunction, optimizationMethod)
                    else:
                        logger.warning("The optimization optimizationMethod does not exist for {0} with {1}.".format(model.name, optimizationParameters['optimizationSetting']))
                        if self.force:
                            continue
                        else:
                            sys.exit("Optimization stops with error.")

                    if self.multiprocess:
                        try:
                            with multiprocessing.Pool() as pool:
                                optimization.bestGuesses = pool.map(optimization.optimizeSingle, (i + 1 for i in range(self.times)))
                        except Exception:
                            logger.exception("{0} with {1} optimization setting fails at multiprocessing".format(model.name, optimizationParameters['optimizationSetting']))
                            if self.force:
                                continue
                            else:
                                sys.exit("Optimization stops with error.")
                    else:
                        for i in range(self.times):
                            try:
                                optimization.bestGuesses.append(optimization.optimizeSingle(i))
                            except Exception:
                                logger.exception("{0} with {1} optimization setting fails at {2} iteration".format(model.name, optimizationParameters['optimizationSetting'], i))
                                if self.force:
                                    continue
                                else:
                                    sys.exit("Optimization stops with error.")

                    # to compress the SAGA optimization results
                    if optimizationMethod == 'SAGA':
                        if os.path.exists(optimization.path + model.name + '_all'):
                            shutil.make_archive(optimization.path + model.name + '_all', 'zip', optimization.path + model.name + '_all')
                            shutil.rmtree(optimization.path + model.name + '_all')
                        if os.path.exists(optimization.path + model.name +'_best'):
                            shutil.make_archive(optimization.path + model.name + '_best', 'zip', optimization.path + model.name + '_best')
                            shutil.rmtree(optimization.path + model.name + '_best')

                    if self.printOptimizationScript:
                        optimization.optimizationScripts()

                    jsonpickle.set_encoder_options('json', sort_keys=True, indent=4)
                    with open('{0}{1}_{2}.json'.format(path, model.name, optimization.optimizationSetting), 'w') as outFile:
                        outFile.write(jsonpickle.encode({'model': model, 'datasets': datasets, 'bestGuesses': optimization.bestGuesses, 'optimizationSetting': optimization.optimizationSetting, 'energyFunction': self.energyFunction}))

            # to store the paths to the optimization results files.
            with open(self.path + '/{0}_{1}.txt'.format(optimizationParameters['optimizationSetting'], self.energyFunction), 'w') as resultsFile:
                for dirpath, _, filenames in os.walk(path):
                    for f in filenames:
                        if f.endswith('{0}.json'.format(optimizationParameters['optimizationSetting'])):
                            resultsFile.write(os.path.abspath(os.path.join(dirpath, f)) + '\n')

    def _initLogging(self):

        """
        To create logger to store optimization process information.
        :return: logging
        """

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(module)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S' )
        fileHandler = logging.FileHandler(self.path + '/logFile.log')
        fileHandler.setFormatter(formatter)
        logging.getLogger().addHandler(fileHandler)
        logging.getLogger().setLevel(logging.INFO)
        return logging