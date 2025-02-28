import sys
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, f1_score, recall_score, precision_score, accuracy_score

def load_data(database_filepath):
    """Load data from sqlite database."""
    engine = create_engine('sqlite:///'+database_filepath)
    df = pd.read_sql('select * from message', con=engine)
    X = df['message']
    Y =  df.iloc[:, 4:]
    category_names = Y.columns.tolist()

    return X, Y, category_names


def tokenize(text):
    """Tokenize a text string, lemmatize resulting words and convert them to lower case.""" 
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    
    clean_tokens =[]
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    
    return clean_tokens


def build_model():
    """Build sklearn pipeline and use graid serach to optmize model.
    """
    vectorizer = CountVectorizer(tokenizer=tokenize)
    tfidf = TfidfTransformer()
    classifier = GradientBoostingClassifier()
    multi_target_classifier = MultiOutputClassifier(classifier)

    pipeline = Pipeline([('vect', vectorizer),
                    ('tfidf', tfidf),
                    ('clf', multi_target_classifier)])
    
    parameters = {
            # 'vect__ngram_range':[(1,1), (1,2)],
            # 'vect__max_df':(0.5, 0.75, 1),
            # 'vect__max_features': (None, 5000, 10000),
             'tfidf__use_idf': (True, False),
             'clf__estimator__n_estimators':(100, 200)
             }
    cv = GridSearchCV(pipeline, param_grid=parameters, cv=3)

    return cv


def evaluate_model(model, X_test, Y_test, category_names):
    """Evaluate model performance with test data, report F1 score, precison, recall and accuracy.
    """
     y_pred = model.predict(X_test)
     for i, c  in enumerate(category_names):
        print('==========='+c+'==========')
        print(classification_report(Y_test[c], y_pred[:, i]))


def save_model(model, model_filepath):
    """Save model to pickle file"""
    pd.to_pickle(model, model_filepath)


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()
