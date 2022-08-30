import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


class Transaction:
    """
    Performs retention rate analysis on input dataframe.

    Parameters:
    -----------
    customer_id : string, name of the column by which individual customer is identified
    transaction_date : string, name of the column which represents transaction date
    automated : bool, default=True, carries out operations automatically; pass False if you want to perform each operation manually
    """

    def __init__(self, df: pd.DataFrame, customer_id: str, transaction_date: str, automated=True):
        self.df = df
        self.customer_id = customer_id
        self.transaction_date = transaction_date

        if automated:
            self.get_cohorts()
            self.calculate_cohort_index()
            retention_rate_df = self.calculate_retention_rate()
            self.visualize_retention_rate(retention_rate_df)

    def get_cohorts(self, period='M'):
        self.df['InvoiceMonth'] = self.df[self.transaction_date].dt.to_period(period)
        self.df['CohortMonth'] = self.df.groupby(self.customer_id)['InvoiceMonth'].transform('min')

    def calculate_cohort_index(self):
        invoice_year, invoice_month = self.df[self.transaction_date].dt.year, self.df[self.transaction_date].dt.month
        cohort_year, cohort_month = self.df['CohortMonth'].dt.year, self.df['CohortMonth'].dt.month
        years_diff = invoice_year - cohort_year
        months_diff = invoice_month - cohort_month
        # Calculate the difference in months and store them in cohort Index column
        self.df['CohortIndex'] = years_diff * 12 + months_diff + 1

    def calculate_retention_rate(self) -> pd.DataFrame:
        # Calculating number of unique customers in each Group of (CohortDate,Index)
        cohort_data = self.df.groupby(['CohortMonth', 'CohortIndex']).CustomerId.nunique().reset_index(
            name='Count of unique CustomerID')
        retention_counts = cohort_data.pivot(index='CohortMonth', columns='CohortIndex',
                                             values='Count of unique CustomerID')
        # Select the first column and store it to cohort_sizes
        cohort_sizes = retention_counts.iloc[:, 0]

        # Divide the cohort count by cohort sizes along the rows
        retention_rate = retention_counts.divide(cohort_sizes, axis=0)

        # Covert the retention rate into percentage and Rounding off.
        retention_rate.round(3) * 100
        return retention_rate

    def visualize_retention_rate(self, retention_rate_df):
        fig, ax = plt.subplots(figsize=(9, 7))
        sns.heatmap(retention_rate_df * 100, annot=True, fmt='0.0f', cmap="BuGn", vmin=0, vmax=50, ax=ax)
        ax.set_title("Retention rates", color='DarkRed')
        ax.set_yticklabels(retention_rate_df.index)
        plt.xlabel('CohortMonth')
        plt.ylabel('CohortIndex')
        plt.show()
