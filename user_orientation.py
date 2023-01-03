import pandas as pd
from haversine import haversine

# 내가 만든 파일 -> test 진행 위해 import
from img_sim import ImgSimilarity
from key_word_sim import KeyWordSimilarit
import TSP

# user 성향을 통한 코스 추천

class UserOrientation:
    # 사용자 성향 값 
    # 0. 유사도 높은 순
    # 1. 최단 거리
    # 2. 인기순위
    # 3. 사람들이 잘 안가는 곳

    def __init__(self, place_list: list, engine):
        self.main_df = pd.read_sql_query("select * from jejudata;", engine)

        self.place_list=place_list
            
    def user_tendency(self, column_name, NOP):
        recommendation_list = []
        for place in self.place_list:
            tmp_num = self.main_df[self.main_df['JejuDataNo'].isin(place)][column_name].values
            tmp_place = self.main_df[self.main_df[column_name] == NOP(tmp_num)].index.to_list()
            tmp_place_id = self.main_df['JejuDataNo'].values[tmp_place]
            recommendation_list.append(tmp_place_id[0])
        recommendation_list.insert(0, "111111")
        return recommendation_list

    # 0. 유사도 높은 순
    def high_similarity(self):
        tmp_recommendation_list = []
        for i in range(len(self.place_list)):
            tmp_recommendation_list.append(self.place_list[i][0])
        tmp_recommendation_list.insert(0, 111111)
        tsp=TSP.TSPAlgorithm(tmp_recommendation_list)

        for i in range(len(tmp_recommendation_list)):
            for j in range(len(tmp_recommendation_list)):
                if i == j:
                    pass
                else:
                    start = (self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[i])]['Latitude'].values, self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[i])]['Longitude'].values)
                    goal = (self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[j])]['Latitude'].values, self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[j])]['Longitude'].values)
                    w = haversine(start, goal)
                    tsp.W[i+1][j+1] = round(w,2)

        opttour=tsp.func()
        return self.result(opttour, tmp_recommendation_list, tsp)
        

    # 1. 최단 거리
    def shortest_distance(self):
        tsp=TSP.Dijkstra(self.place_list)
        # 시작 노드 번호 입력
        start = 0

        for i in range(len(tsp.tmp_places)):
            for j in range(len(tsp.tmp_places)):
                if i == j:
                    pass
                else:
                    st = (self.main_df[self.main_df['JejuDataNo'] == tsp.tmp_places[i]]['Latitude'].values, self.main_df[self.main_df['JejuDataNo'] == tsp.tmp_places[i]]['Longitude'].values)
                    go = (self.main_df[self.main_df['JejuDataNo'] == tsp.tmp_places[j]]['Latitude'].values, self.main_df[self.main_df['JejuDataNo'] == tsp.tmp_places[j]]['Longitude'].values)
                    w = haversine(st, go)
                    tsp.graph[i].append((j, round(w,2)))

        path = []
        path.append(start)
        sum_length = 0
        # 다익스트라 알고리즘 수행
        while True:
            #print(start)
            tsp.dijkstra(start)
            min_num = 0
            tmp_distance = sorted(tsp.distance[1:-1])
            min_length = tmp_distance[min_num]
            min_index = tsp.distance.index(min_length)

            while True:
                if min_index in path:
                    min_num += 1   
                    min_length = tmp_distance[min_num]
                    min_index = tsp.distance.index(min_length)
                    continue
                else:
                    duplicate_path = 0
                    for i in path:
                        if tsp.group_dic[i] == tsp.group_dic[min_index]:
                            duplicate_path += 1

                    if 0 != duplicate_path:
                        min_num += 1
                        min_length = tmp_distance[min_num]
                        min_index = tsp.distance.index(min_length)
                    else:
                        min_length = tmp_distance[min_num]
                        sum_length += min_length
                        path.append(tsp.distance.index(min_length))
                        break
            start = path[-1]
            if len(path) == len(self.place_list) + 1:
                break

        path.append(0) 
        final_recommendation_list=[]
        for i in range(len(path)):
            final_recommendation_list.append(tsp.tmp_places[path[i]])
        final_length = round(sum_length)
        return final_recommendation_list[1:-1], final_length


    # 2. 인기순위 - po=popilarity
    # 3. 사람들이 잘 안가는 곳
    def popularity_ranking(self, po):
        if po=="popularity":
            tmp_recommendation_list = self.user_tendency('lookup_num', max)
        else:
            tmp_recommendation_list = self.user_tendency('time_sum', min)
        tsp=TSP.TSPAlgorithm(tmp_recommendation_list)
        # 간선의 정보
        for i in range(len(tmp_recommendation_list)):
            for j in range(len(tmp_recommendation_list)):
                if i == j:
                    pass
                else:
                    start = (self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[i])]['Latitude'].values, self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[i])]['Longitude'].values)
                    goal = (self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[j])]['Latitude'].values, self.main_df[self.main_df['JejuDataNo'] == int(tmp_recommendation_list[j])]['Longitude'].values)
                    w = haversine(start, goal)
                    tsp.W[i+1][j+1] = round(w,2)
        
        opttour=tsp.func()
        return self.result(opttour, tmp_recommendation_list, tsp)

    def result(self, opttour, tmp_recommendation_list, tsp):
        final_recommendation_list=[]
        for i in range(len(opttour)):
            final_recommendation_list.append(tmp_recommendation_list[opttour[i]-1])

        return final_recommendation_list[1:-1], round(tsp.minlength)

if __name__ == "__main__":
    # row 생략 없이 출력
    test_user=["0", "1", "2"]
    area=['제주시']
    pre_df=KeyWordSimilarit(test_user, area).re_df()
    a=ImgSimilarity(pre_df, 7)
    a.make_cosine_sim()
    test=a.make_user_place_df()
    b=UserOrientation(test)
    idx, dis = b.high_similarity()
    print(idx, f"거리 : {dis}km")

    t,d =b.shortest_distance()
    print(t, f"거리 : {d}km")

    t2,d2=b.popularity_ranking("popularity")
    print(t2, f"거리 : {d2}km")

    t3,d3=b.popularity_ranking("unpopularity")
    print(t3, f"거리 : {d3}km")
