# coding: utf-8
"""
GAを使って3Dconv-Netのハイパラ探索
"""

import numpy as np
import argparse
import random
from deap import base, creator, tools, algorithms

import conv3d

def genAlg(population=5, CXPB=0.5, MUTPB=0.2, NGEN=5):
    random.seed(64)
    pop = toolbox.population(n=population)

    print("start of evolution")

    # 初期集団の個体を評価
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    print(" %i の個体を評価 " % len(pop))

    # 進化計算
    for g in range(NGEN):
        print(" -- %i 世代 --" % g)

        """ 選択 """
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        """ 交叉 """
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                print("mate")
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        
        """ 変異 """
        for mutant in offspring:
            if random.random() < MUTPB:
                print("mutate")
                toolbox.mutate(mutant)
                del mutant.fitness.values
        
        try:
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
        except AssertionError:
            pass

        print(" %i の個体を評価" % len(invalid_ind))

        pop[:] = offspring
        try:
            fits = [ind.fitness.values[0] for ind in pop]
            
            length = len(pop)
            mean = sum(fits)/length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            
            print(" Min %s " % min(fits))
            print(" Max %s " % max(fits))
            print(" Avg %s " % mean)
            print(" Std %s " % std)
        except IndexError:
            pass

    print("-- 進化終了 --")

    best_ind = tools.selBest(pop, 1)[0]
    print(" 最も優れていた個体 %s %s " % (best_ind, best_ind.fitness.values))
    return best_ind


def run_conv3d(bounds):
    _conv3d = conv3d.Conv3DNet(conv1=bounds[0],
                                conv2=bounds[1],
                                conv3=bounds[2],
                                conv4=bounds[3],
                                conv5=bounds[4],
                                dense1=bounds[5],
                                dense2=bounds[6],
                                dropout=bounds[7],
                                bn1=bounds[8],
                                bn2=bounds[9],
                                batch_size=bounds[10],
                                opt=bounds[11]
                                )
    conv3d_evaluation = _conv3d.conv3d_evaluate()

""" define Genetic Algorithm """

# 適応度クラス作成
creator.create('FitnessMax', base.Fitness, weights=(-1.0,))
creator.create('Individual', list, fitness=creator.FitnessMax)

# define attributes for individual
toolbox = base.Toolbox()

# 各パラメータを生成する関数を定義

# 畳込み層のフィルタサイズ
toolbox.register("conv1", random.choice, (8, 16, 32, 64, 128, 256, 512))
toolbox.register("conv2", random.choice, (8, 16, 32, 64, 128, 256, 512))
toolbox.register("conv3", random.choice, (8, 16, 32, 64, 128, 256, 512))
toolbox.register("conv4", random.choice, (8, 16, 32, 64, 128, 256, 512))
toolbox.register("conv5", random.randint, 0, 1)

toolbox.register("dense1", random.choice, (16, 32, 64, 128, 256, 512, 1024))
toolbox.register("dense2", random.choice, (16, 32, 64, 128, 256, 512, 1024))

toolbox.register("dropout", random.uniform, 0.0, 0.8)
toolbox.register("bn1", random.randint, 0, 1)
toolbox.register("bn2", random.randint, 0, 1)

toolbox.register("batch_size", random.choice, (8, 16, 32, 64, 128))
toolbox.register("opt", random.choice, ('sgd', 'rmsprop', 'adam'))

# registar attributes to individual
toolbox.register('individual', tools.initCycle, creator.Individual,
                (toolbox.conv1, toolbox.conv2, toolbox.conv3, toolbox.conv4, toolbox.conv5,
                toolbox.dense1, toolbox.dense2,
                toolbox.dropout, toolbox.bn1, toolbox.bn2,
                toolbox.batch_size, toolbox.opt),
                n=1)

# individual to population
toolbox.register('population', tools.initRepeat, list, toolbox.individual)

toolbox.register('mate', tools.cxTwoPoint)
toolbox.register('select', tools.selTournament, tournsize=3)
toolbox.register('evaluate', run_conv3d)

best_int = genAlg(population=5, CXPB=0.5, MUTPB=0.2, NGEN=10)