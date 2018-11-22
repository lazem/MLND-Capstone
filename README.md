# MLND Deep Learning Capstone
Detecting Duplicate URLs Using Deep Recurrent Networks

## Source Code
This is a breakdown of the code sections:
- `01-Content Crawler`
- `02-Similarity Scoring`
- `03-Exploratory Analysis and Data Preparation`
- `04-Model Training and Evaluation`


## Requirements

This project requires **Python 3.5+** and the following libraries installed:

- [Scrapy](https://scrapy.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [NumPy](http://www.numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [jusText](https://github.com/miso-belica/jusText)
- [HTML Similarity](https://github.com/matiskay/html-similarity)
- [Scikit-learn](http://scikit-learn.org/stable/)
- [matplotlib](http://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [TensorFlow](http://www.tensorflow.org/)
- [Keras](https://keras.io/)
- [Six](http://pypi.python.org/pypi/six/)


For model training, a GPU-based machine is required. To run the jupyter notebooks, a software should be installed to run and execute an [iPython Notebook](http://ipython.org/notebook.html)


## Data

The datasets are collected from different open sites, crawling a subset sample from each to train the algorithm. The following sites are the ones used:

-	https://ubuntuforums.org
-	https://digitalspy.com
-	http://forums.mozillazine.org
-	https://bodybuilding.com

![barplot](https://github.com/lazem/MLND-Capstone/blob/master/Proposal/images/barplot.png)


 ## Result

This is the final model accuracy and loss result history, across the four training and validation sets.

![result](https://github.com/lazem/MLND-Capstone/blob/master/Proposal/images/result.png)

