'''
inventoryanalytics: a Python library for Inventory Analytics

Author: Roberto Rossi

MIT License
  
Copyright (c) 2018 Roberto Rossi
'''

import csv
import numpy as np
from typing import List
from scipy.optimize import linprog
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import StandardScaler 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, confusion_matrix    

class abc:

    def __init__(self, file='./inventoryanalytics/abc/data/Flores1992.csv'):
        self.data = abc.readData(file)

    @staticmethod
    def annotate_ABC(m):
        """
        Annotate matrix with ABC
        
        Arguments:
            m -- the matrix
        
        Returns:
            the annotated matrix
        """

        proportion = lambda p, k: k/len(m) < p
        class_breakpoints = {'A': 0.2, 'B': 0.5, 'C': 1}
        for k in range(0,len(m)):
            if proportion(class_breakpoints['A'],k):
                m[k].append('A') 
            elif proportion(class_breakpoints['B'],k): 
                m[k].append('B')
            else: 
                m[k].append('C')
        return m

    @staticmethod
    def annual_dollar_usage_instance():
        # prepare data
        d = abc()
        data = d.data
        '''
        TAU -- Total Annual Usage
        AUC -- Average Unit Cost ($)
        ADU -- Annual Dollar Usage ($)
        A%U -- Annual % Usage
        C   -- Criticality factor
        LT  -- Lead time
        ABC -- ABC classification
        
        data = [
            ['Item', 'TAU', 'AUC', 'ADU', 'Cum. ADU', 'Cum. A%U', 'C', 'LT', 'ABC'], 
            ['s1', '117', '49.92', '5840.64', '5840.64', '11.3', '1', '2', 'A'], 
            ['s2', '27', '210', '5670', '11510.64', '22.3', '1', '5', 'A'],
            ...
            ]
        '''

        item_no = np.matrix(data)[1:,0]                #item ids
        m = np.matrix(data)[1:,[1,2]].astype(np.float) #criteria scores

        # compute ADU
        adu = [[item_no[k,0],m[k,0]*m[k,1]] for k in range(0,len(m))]
        
        # append ADU classes
        for k in range(0,len(adu)):
            adu[k].append(data[k+1][8])

        adu = sorted(adu,key=lambda x: x[1], reverse=True)

        # annotate ABC
        abc.annotate_ABC(adu)

        unsorted_adu = sorted(adu,key=lambda x: int(x[0][1:]), reverse=False)

        print(np.matrix(unsorted_adu))
        
        x, y = 1, 2 #1,2,6,7
        abc.abc_scatter_labels([row[3] for row in unsorted_adu], x, y)

    @staticmethod
    def ahp_instance():
        # prepare data
        d = abc()
        data = d.data

        item_no = np.matrix(data)[1:,0]                     #item ids
        m = np.matrix(data)[1:,[1,2,6,7]].astype(np.float)  #criteria scores

        #weights for average unit cost, annual dollar usage, criticality, lead time
        w = [0.078,0.092,0.42,0.41] 

        # compute AHP
        fmin, fmax = m.min(0), m.max(0)
        norm = lambda i, v : (v-fmin[0,i])/(fmax[0,i]-fmin[0,i])
        ahp = [[item_no[k,0],sum(w[i]*norm(i, m[k,i]) for i in range(0,4))] for k in range(0,len(m))]
        
        # append ADU classes
        for k in range(0,len(ahp)):
            ahp[k].append(data[k+1][8])

        ahp = sorted(ahp,key=lambda x: x[1], reverse=True)

        # annotate ABC
        abc.annotate_ABC(ahp)

        unsorted_ahp = sorted(ahp,key=lambda x: int(x[0][1:]), reverse=False)

        print(np.matrix(unsorted_ahp))
        
        x, y = 1, 2 #1,2,6,7
        abc.abc_scatter_labels([row[3] for row in unsorted_ahp], x, y)

    @staticmethod
    def dea_instance(scaled: bool):
        # prepare data
        d = abc()
        data = d.data

        item_no = np.matrix(data)[1:,0]                       #item ids
        m = np.matrix(data)[1:,[1,2,6,7]].astype(np.float)    #criteria scores

        # compute DEA
        fmin, fmax = m.min(0), m.max(0)
        norm = lambda j, v : ((v-fmin[0,j])/(fmax[0,j]-fmin[0,j]) if scaled else v)
        lp_m = [[norm(j,m[k,j]) for j in range(0,np.size(m,1))] 
                for k in range(0,np.size(m,0))]
        lp = lambda i, lp_matrix : -linprog([-k for k in lp_matrix[i]], 
                                            lp_matrix, 
                                            [1 for k in range(0,len(lp_matrix))]).fun
        dea = [[item_no[k,0],lp(k, lp_m)] for k in range(0,len(lp_m))]

        # append ADU classes
        for k in range(0,np.size(m,0)):
            dea[k].append(d.data[k+1][8])

        dea = sorted(dea,key=lambda x: x[1], reverse=True)

        # annotate ABC
        abc.annotate_ABC(dea)

        unsorted_dea = sorted(dea,key=lambda x: int(x[0][1:]), reverse=False)

        print(np.matrix(unsorted_dea))
        
        x, y = 1, 2 #1,2,6,7
        abc.abc_scatter_labels([row[3] for row in unsorted_dea], x, y)

    @staticmethod
    def k_nn_example():

        # prepare data
        d = abc('./inventoryanalytics/abc/data/training_knn.csv')
        data = d.data

        X = np.matrix(data)[1:,[1,2]]
        Y = np.matrix(data)[1:,8]

        scaler = StandardScaler()  
        scaler.fit(X)
        X = scaler.transform(X)

        classifier = KNeighborsClassifier(n_neighbors=3) 
        classifier.fit(X, Y) 

        point = scaler.transform(np.matrix([[3, 60.6]]))
        Y_pred = classifier.predict(point)
        print(Y_pred)

        my_colors = {'A':'red','B':'yellow','C':'green'}
        for k in range(0,X.shape[0]-1):
            plt.scatter(X[:,0].flatten().tolist()[k],
                        X[:,1].flatten().tolist()[k],
                        color = my_colors.get(Y.flatten().tolist()[0][k]))
            plt.annotate(Y.flatten().tolist()[0][k],
                         (X[:,0].flatten().tolist()[k],
                          X[:,1].flatten().tolist()[k]))
        
        plt.scatter(point[:,0].flatten().tolist()[0],
                    point[:,1].flatten().tolist()[0],
                    color = 'blue')
        plt.annotate(Y_pred[0],
                     (point[:,0].flatten().tolist()[0],
                      point[:,1].flatten().tolist()[0]))

        # plot label and grid
        x, y = 1, 2
        plt.xlabel(np.matrix(data)[0,x])
        plt.ylabel(np.matrix(data)[0,y])
        plt.grid(True)
        # show plot
        plt.show()

    @staticmethod
    def k_nn():
        # http://stackabuse.com/k-nearest-neighbors-algorithm-in-python-and-scikit-learn/

        # prepare data
        d = abc()
        data = d.data

        item_no = np.matrix(data)[1:,0]                       #item ids
        X = np.matrix(data)[1:,[1,2,6,7]]
        Y = np.matrix(data)[1:,8]
        
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.20)  

        scaler = StandardScaler()  
        scaler.fit(X_train)
        X_train = scaler.transform(X_train)  
        X_test = scaler.transform(X_test) 

        classifier = KNeighborsClassifier(n_neighbors=3) 
        classifier.fit(X_train, Y_train)  

        Y_pred = classifier.predict(X_test)  

        print(confusion_matrix(Y_test, Y_pred))  
        print(classification_report(Y_test, Y_pred))  

        labels = classifier.predict(scaler.transform(X))  
        
        matrix = [[item_no[k,0],X[k,0],X[k,1],X[k,2],X[k,3],labels[k]] for k in range(0,len(X))]
        print(np.matrix(matrix))
        
        x, y = 1, 2 #1,2,6,7
        abc.abc_scatter_labels(labels, x, y)

    @staticmethod
    def pca():
        # prepare data
        d = abc()
        data = d.data

        item_no = np.matrix(data)[1:,0]                     #item ids
        m = np.matrix(data)[1:,[2,3,6,7]].astype(np.float)  #criteria scores

        cov_mat = np.cov(m, rowvar=False)
        np.set_printoptions(precision=5, suppress=True)
        print(cov_mat)
        eig_vals, eig_vecs = np.linalg.eig(cov_mat)
        print(eig_vals)
        print(eig_vecs)
        w = np.asarray(eig_vecs[:,0])
        print(w)

        # compute PCA
        fmin, fmax = m.min(0), m.max(0)
        norm = lambda i, v : (v-fmin[0,i])/(fmax[0,i]-fmin[0,i])
        pca = [[item_no[k,0],sum(w[i]*norm(i, m[k,i]) for i in range(0,4))] for k in range(0,len(m))]
        
        # append ADU classes
        for k in range(0,len(pca)):
            pca[k].append(data[k+1][8])

        pca = sorted(pca,key=lambda x: x[1], reverse=True)

        # annotate ABC
        abc.annotate_ABC(pca)

        unsorted_ahp = sorted(pca,key=lambda x: int(x[0][1:]), reverse=False)

        print(np.matrix(unsorted_ahp))
        
        x, y = 1, 2 #1,2,6,7
        abc.abc_scatter_labels([row[3] for row in unsorted_ahp], x, y)

    @staticmethod
    def abc_scatter_labels(labels, x, y):
        # prepare data
        d = abc()
        # print(np.matrix(d.data))
        # plot points and annotations
        m = np.matrix(d.data)[1:,[x,y]].astype(np.float)
        my_colors = {'A':'red','B':'yellow','C':'green'}
        for k in range(0,m.shape[0]-1):
            plt.scatter(m[:,0].flatten().tolist()[0][k],
                        m[:,1].flatten().tolist()[0][k],
                        color = my_colors.get(labels[k]))
            plt.annotate(labels[k],#np.matrix(d.data)[k+1,0] +": "+ labels[k], 
                         (m[:,0].flatten().tolist()[0][k],
                          m[:,1].flatten().tolist()[0][k]))
        # plot label and grid
        plt.xlabel(np.matrix(d.data)[0,x])
        plt.ylabel(np.matrix(d.data)[0,y])
        plt.grid(True)
        # show plot
        plt.show()

    @staticmethod
    def readData(file: str):
        d = []
        with open(file) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                d.append(row)
        return d

if __name__ == '__main__':
    abc_strategy = 'ADU'

    if abc_strategy == 'ADU':
        abc.annual_dollar_usage_instance()
    elif abc_strategy == 'AHP':
        abc.ahp_instance()
    elif abc_strategy == 'DEA':
        scaled = False
        abc.dea_instance(scaled)
    elif abc_strategy == 'kNN':
        #abc.k_nn_example()
        abc.k_nn()
    elif abc_strategy == 'PCA':
        abc.pca()
    
    