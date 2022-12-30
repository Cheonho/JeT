import pandas as pd
import heapq
from copy import deepcopy
from haversine import haversine
import numpy as np

# 내가 만든 파일 -> test 진행 위해 import
from img_sim import ImgSimilarity
from key_word_sim import KeyWordSimilarit
df=pd.read_csv("./data/visit_jeju_merge_data_v13.csv", encoding='cp949')

# user 성향을 통한 코스 추천

class UserOrientation:
    def __init__(self, place_list: list):
        self.place_list=place_list
            
    def user_tendency(self, column_name, NOP, df):
        recommendation_list = []
        for place in self.place_list:
            tmp_num = df[df['place_id'].isin(place)][column_name].values
            tmp_place = df[df[column_name] == NOP(tmp_num)].index.to_list()
            tmp_place_id = df['place_id'].values[tmp_place]
            recommendation_list.append(str(tmp_place_id[0]))
        recommendation_list.insert(0, "111111")
        return recommendation_list

if __name__ == "__main__":
    # row 생략 없이 출력
    test_user=["0", "1", "2"]
    pre_df=KeyWordSimilarit(test_user).re_df()
    a=ImgSimilarity(pre_df)
    a.make_cosine_sim()
    test=a.make_user_place_df()
    b=UserOrientation(test)

    # 조회수 가장 높음
    print(f"조회수 가장 높음 : {b.user_tendency('lookup_num', max, df)}")

    #조회수 가장 낮은 거
    print(f"조회수 가장 낮음 : {b.user_tendency('lookup_num', min, df)}")

    #사람 많은 순
    print(f"람 많은 순 : {b.user_tendency('time_sum', max, df)}")

    #사람 적은 순
    print(f"람 적은 순 : {b.user_tendency('time_sum', min, df)}")

