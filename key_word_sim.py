import pandas as pd
import numpy as np

# 키워드 유사도

place_df=pd.read_csv('./data/normalized_place_matrix.csv')
place_df_drop=place_df.drop(['place_name','total_count','place_id'], axis=1)

class KeyWordSimilarit:
    def __init__(self, keyword: list):
        self.user=[0.0 for i in range(5)]
        for idx, val in enumerate(place_df_drop.columns):
            if val in keyword:
                self.user[idx]=1
        self.result=np.dot(place_df_drop, self.user)

    def re_df(self):
        place_df['preference'] = self.result
        place_df.sort_values(['preference'], axis=0, ascending=False, inplace=True)
        return place_df

if __name__ == "__main__":
    # row 생략 없이 출력
    pd.set_option('display.max_rows', None)
    test_user=["0", "1", "2"]
    a=KeyWordSimilarit(test_user).re_df()
    print(a)
