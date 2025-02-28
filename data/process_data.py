import sys
import numpy as np
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    """ Load messages and categories files.
    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    #merge datasets
    df = messages.merge(categories, how='inner', on='id')
    # create a dataframe of the 36 individual category columns
    categories = df.categories.str.split(';', expand=True)
    # select the first row of the categories dataframe
    row = categories.iloc[0]
    # use this row to extract a list of new column names for categories.
    category_colnames = row.str.split('-').str.get(0)
    # rename the columns of `categories`
    categories.columns = category_colnames
    #convert category values to numbers 0 or 1
    categories = categories.applymap(lambda x: int(x[-1]))
    # drop the original categories column from `df` 
    # concatenate the original dataframe with the new `categories` dataframe
    df.drop('categories', axis=1, inplace=True)
    df = pd.concat([df, categories], axis=1)

    return df



def clean_data(df):
    """Clean data. Remove duplicates and columns with a single value.
    """
    #remove duplicates
    df.drop_duplicates(inplace=True)
    #remove columns with only a single value
    col_with_more_vals = df.apply(lambda x: len(pd.unique(x))) > 1
    df = df.loc[:, col_with_more_vals]
    return df


def save_data(df, database_filename):
    """Save dataframe to sqlite database."""
    engine = create_engine('sqlite:///'+database_filename)
    df.to_sql('Message', engine, index=False)      


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
