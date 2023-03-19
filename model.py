import numpy as np
import pandas as pd
from sklearn import svm
from sklearn.model_selection import train_test_split

ex = pd.read_csv('./assets/synthetic_control_data.csv', delim_whitespace=True, header=None)
xdf = pd.DataFrame(columns=['mean', 'std', 'skew', 'kurt', 'label'])
xdf['mean'] = np.mean(ex, axis=1)
xdf['std'] = np.std(ex, axis=1)
xdf['skew'] = ex.skew(axis=1)
xdf['kurt'] = ex.kurt(axis=1)
xdf['label'].iloc[0:100] = 'normal'
xdf['label'].iloc[100:201] = 'cyclic'
xdf['label'].iloc[201:301] = 'increasing_trend'
xdf['label'].iloc[301:401] = 'decreasing_trend'
xdf['label'].iloc[401:501] = 'upward_shift'
xdf['label'].iloc[501:] = 'downward_shift'
X = np.asarray(xdf[['mean', 'std', 'skew', 'kurt']])
y = np.asarray(xdf['label'])
## Support Vector Machines (SVM)
classifier = svm.SVC(kernel='linear', gamma='auto', C=2)
classifier.fit(X, y)

def findTrend(test_data):
    if "sample_size" in test_data.columns:
        test_data[1]=test_data[1]/test_data['sample_size']
        test_data = test_data.drop(['sample_size'], axis=1)
        test_data = test_data.drop(['Sample'], axis=1)
        test_data.columns = pd.RangeIndex(0, len(test_data.columns)) 
    else:
        test_data = test_data.drop(['Sample'], axis=1)
        test_data.columns = pd.RangeIndex(0, len(test_data.columns)) 

    test_data['mean_0'] = np.mean(test_data, axis=1) 
    test_data = test_data.drop(columns=test_data.columns[0:-1], axis=1)
    test_df = pd.DataFrame(columns=['mean', 'std', 'skew', 'kurt'])
    test_df['mean'] = np.mean(test_data, axis=0)
    test_df['std'] = np.std(test_data, axis=0)
    test_df['skew'] = test_data.skew(axis=0)
    test_df['kurt'] = test_data.kurt(axis=0)
    test_df= test_df.to_numpy()
    test_predict=classifier.predict(test_df)
    return test_predict[0]
