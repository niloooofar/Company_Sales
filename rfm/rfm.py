import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from rfm.helper import get_quantile


class RFM:
    """
    Performs RFM analysis and customer segmentation on input dataframe.

    Attributes:
    -----------
    rfm_table : dataframe with unique customers with their rfm values/scores
    segment_table : dataframe with count of customers across all segments
    Parameters:
    -----------
    customer_id : string, name of the column by which individual customer is identified
    transaction_date : string, name of the column which represents transaction date
    amount : string, column stating amount of transaction
    automated : bool, default=True, carries out operations automatically; pass False if you want to perform each operation manually
    """

    def __init__(self, df: pd.DataFrame, customer_id: str, transaction_date: str, amount: str, automated=True):
        self.df = df
        self.customer_id = customer_id
        self.transaction_date = transaction_date
        self.amount = amount

        if automated:
            self.df = self.preprocess_data()
            self.df = self.calculate_rfm()
            self.rfm_table = self.segment_customers()
            self.segment_table = self.produce_segment_df()

    def get_rfm_table(self):
        return self.rfm_table[['CustomerId', 'RFM', 'segment']]

    def preprocess_data(self) -> pd.DataFrame:
        self.df.dropna(subset=[self.amount, self.customer_id], inplace=True)
        self.df.drop_duplicates(inplace=True)
        self.df = self.df[self.df.amount > 0]
        return self.df

    def calculate_rfm(self) -> pd.DataFrame:
        df_grp = self.df[[self.customer_id, self.transaction_date, self.amount]].groupby(self.customer_id).agg(
            list).reset_index()
        latest_date = self.df[self.transaction_date].max()
        self.df = self.df.sort_values(by=self.transaction_date, na_position='first')
        # finding r,f,m values
        df_grp['recency'] = df_grp[self.transaction_date].apply(lambda x: (latest_date - x[-1]).days)
        df_grp['frequency'] = df_grp[self.amount].apply(len)
        df_grp['monetary_value'] = df_grp[self.amount].apply(sum)
        # finding r,f,m quartile
        r1, r2, r3 = np.quantile(df_grp.recency, [0.25, 0.5, 0.75])
        f1, f2, f3 = np.quantile(df_grp.frequency, [0.25, 0.5, 0.75])
        m1, m2, m3 = np.quantile(df_grp.monetary_value, [0.25, 0.5, 0.75])
        # assigning r,f,m quartile
        df_grp['R_quartile'] = df_grp.recency.apply(get_quantile, args=(r1, r2, r3))
        df_grp['F_quartile'] = df_grp.recency.apply(get_quantile, args=(f1, f2, f3))
        df_grp['M_quartile'] = df_grp.recency.apply(get_quantile, args=(m1, m2, m3))
        df_grp['RFM'] = df_grp['R_quartile'] * 100 + df_grp['F_quartile'] * 10 + df_grp['M_quartile']
        df_grp['RFM'] = df_grp['RFM'].astype('str')
        return df_grp

    @staticmethod
    def get_rfm_segment(arr):
        segment = 'Normal'
        if arr[2] == '4':
            segment = 'BigSpenders'
        if arr[1] == '4':
            segment = 'Loyal'
        if arr == '441':
            segment = 'LostCheap'
        if arr == '444':
            segment = 'LostBigSpenders'
        if arr == '344':
            segment = 'AlmostLost'
        if arr == '144':
            segment = 'Best'
        return segment

    def segment_customers(self) -> pd.DataFrame:
        self.df['segment'] = self.df.RFM.apply(self.get_rfm_segment)
        return self.df

    def produce_segment_df(self) -> pd.DataFrame:
        segment_df = self.df[['segment', self.customer_id]].groupby('segment').count().reset_index().rename(
            {self.customer_id: 'no of customers'}, axis=1)
        return segment_df

    def find_customers(self, segment: str) -> pd.DataFrame:
        return self.rfm_table[self.rfm_table['segment'] == segment].reset_index(drop=True)[self.customer_id].values

    def plot_segment_bar(self):
        segment_df = self.df[['segment', self.customer_id]].groupby('segment').count().reset_index().rename(
            {self.customer_id: 'no of customers'}, axis=1)
        x = segment_df['segment'][::-1]
        y = segment_df['no of customers'][::-1]
        plt.figure(figsize=(4, 4))
        plt.barh(x, y, edgecolor='black', color='darkkhaki')
        plt.xlabel('No of Customers', color='orange')
        plt.ylabel('Segment', color='orange')
        plt.title('Segment Distribution', color = 'red')
        plt.grid()
        plt.show()
        
    def plot_segment_pie(self):
        segment_df = self.df[['segment', self.customer_id]].groupby('segment').count().reset_index().rename(
            {self.customer_id: 'no of customers'}, axis=1)
        x = segment_df['segment'][::-1]
        y = segment_df['no of customers'][::-1]
        plt.figure(figsize=(4, 4))
        plt.pie(y, labels=x, autopct='%.1f',  textprops={'fontsize': 10})
        plt.title('Customer Segments Distribution', fontsize=14, color='green')
        plt.show()

