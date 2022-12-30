import pandas as pd
import heapq
from copy import deepcopy
from haversine import haversine
import numpy as np

# 내가 만든 파일 -> test 진행 위해 import
from user_orientation import UserOrientation
from img_sim import ImgSimilarity
from key_word_sim import KeyWordSimilarit

df=pd.read_csv("./data/visit_jeju_merge_data_v13.csv", encoding='cp949')

# TSP 알고리즘
#  - 최단 거리 간선의 정보 확인

class Node:
    bound = 0
    def __init__(self, level: int, path: list):
        self.level = level
        self.path = path


class TSPAlgorithm:
    def __init__(self, tmp_recommendation_list) -> None:
        self.INF = 9999
        self.minlength=self.INF
        self.n = len(tmp_recommendation_list)
        self.m = self.n * (self.n-1)
        self.W = [[self.INF] * (self.n + 1) for _ in range(self.n + 1)] 
        for i in range(self.n + 1):
            self.W[i][i] = 0

    def length(self, path: list) -> int:
        # len = 0
        # i = 0
        # while path[i] != path[-1]:
        #     if path[i] != path[-2]:
        #         len += W[path[i]][path[i + 1]]
        #     i += 1
        # return len
        p_len = 0
        i = 0
        for i in range(0, len(path) - 1):
            p_len += self.W[path[i]][path[i + 1]]
        return p_len


    def hasOutgoing(self,v: int, path: list) -> bool:
        # i = 0
        # while path[i] != path[-2]:
        #     if path[i] == v:
        #         return True
        #     i += 1
        # return False
        temp = path[:-1]
        if v in temp:
            return True
        return False


    def hasIncoming(self, v: int, path: list) -> bool:
        # i = 1
        # while path[i] != path[-1]:
        #     if path[i] == v:
        #         return True
        #     i += 1
        # return False
        temp = path[1:]
        if v in temp:
            return True
        return False


    def bound(self, v: Node) -> int:
        lower = self.length(v.path)
        for i in range(1, self.n + 1):
            if self.hasOutgoing(i, v.path):
                continue
            min = self.INF
            for j in range(1, self.n + 1):
                if i == j:
                    continue
                if j == 1 and i == v.path[-1]:
                    continue
                if self.hasIncoming(j, v.path):
                    continue
                if min > self.W[i][j]:
                    min = self.W[i][j]

            lower += min
            if lower >= self.INF:
                return self.INF

        return lower


    def remaining_vertex(self, path: list) -> int:
        total = self.n * (self.n + 1) // 2
        total_path = sum(path)

        return total - total_path


    def func(self) -> None:
        cnt = 0
        PQ = []
        opttour=[]
        v = Node(0, [1])
        v.bound = self.bound(v)

        # print(v.level, v.bound, *v.path, sep=' ')

        heapq.heappush(PQ, (v.bound, cnt, v))

        while len(PQ):
            v = heapq.heappop(PQ)[2]
            if v.bound < self.minlength:
                for i in range(2, self.n + 1):
                    cnt += 1
                    if i in v.path:
                        continue
                    u = Node(v.level + 1, deepcopy(v.path))
                    u.path.append(i)
                    if u.level == self.n - 2:
                        u.path.append(self.remaining_vertex(u.path))
                        u.path.append(1)
                        if self.length(u.path) < self.minlength:
                            self.minlength = self.length(u.path)
                            opttour = u.path.copy()
                    else:
                        u.bound = self.bound(u)
                        if u.bound < self.minlength:
                            try:
                                heapq.heappush(PQ, (u.bound, cnt, u))
                            finally:
                                pass

                    # if u.level > self.n - 3:
                    #     if self.length(u.path) >= self.INF:
                    #         print(u.level, "INF", *u.path, sep=' ')
                    #     else:
                    #         print(u.level, self.length(u.path), *u.path, sep=' ')
                    # else:
                    #     if u.bound >= self.INF:
                    #         print(u.level, "INF", *u.path, sep=' ')
                    #     else:
                    #         print(u.level, u.bound, *u.path, sep=' ')
        return opttour


if __name__ == "__main__":

    # row 생략 없이 출력
    test_user=["0", "1", "2"]
    pre_df=KeyWordSimilarit(test_user).re_df()
    a=ImgSimilarity(pre_df)
    a.make_cosine_sim()
    test=a.make_user_place_df()
    b=UserOrientation(test)

    # n, m = map(int, input().split())        # 정점과 간선의 개수
    tmp_recommendation_list=b.user_tendency('lookup_num', max, df)
    tsp=TSPAlgorithm(tmp_recommendation_list)
    # opttour = []

    # n = len(tmp_recommendation_list)
    # print(n)
    # m = n * (n-1)
    # print(m)
    # W = [[INF] * (n + 1) for _ in range(n + 1)]       # 인접행렬

    # for i in range(n + 1):
    #     W[i][i] = 0
    
    # 간선의 정보
    for i in range(len(tmp_recommendation_list)):
        for j in range(len(tmp_recommendation_list)):
            if i == j:
                pass
            else:
                start = (df[df['place_id'] == int(tmp_recommendation_list[i])]['Latitude'].values, df[df['place_id'] == int(tmp_recommendation_list[i])]['Longitude'].values)
                goal = (df[df['place_id'] == int(tmp_recommendation_list[j])]['Latitude'].values, df[df['place_id'] == int(tmp_recommendation_list[j])]['Longitude'].values)
                w = haversine(start, goal)
                tsp.W[i+1][j+1] = round(w,2)
    opttour=tsp.func()

    print("최소 거리 : ",round(tsp.minlength),"km")
    print("간선의 정보 : ",*opttour, sep=' ')

    final_recommendation_list = []
    for i in range(len(opttour)):
        final_recommendation_list.append(tmp_recommendation_list[opttour[i]-1])
    print("최종 코스 list(공항포함) : ",final_recommendation_list)  # 111111은 제주공항
    print("최종 코스 list(공항제외) : ",final_recommendation_list[1:-1])