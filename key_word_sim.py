import pandas as pd
import numpy as np

# 키워드 유사도

place_df=pd.read_csv('./data/normalized_place_matrix.csv')
# place_df_drop=place_df.drop(['place_name','total_count','place_id'], axis=1)

class KeyWordSimilarit:
    def __init__(self, keyword: list, area):
        self.place_df_area=place_df[place_df['area'].isin(area)]
        place_df_drop=self.place_df_area.drop(['place_name','total_count','place_id', 'area'], axis=1)
        self.user=[0.0 for i in range(5)]
        for idx, val in enumerate(place_df_drop.columns):
            if val in keyword:
                self.user[idx]=1
        self.result=np.dot(place_df_drop, self.user)

    def re_df(self):
        self.place_df_area['preference'] = self.result
        self.place_df_area.sort_values(['preference'], axis=0, ascending=False, inplace=True)
        return self.place_df_area

    def day(self, start_day, end_day, start_time, end_time):
        # 마지막 날 여행 시작 시간
        travel_start_time = 9
        # 첫 날 여행 종료 시간
        travel_end_time = 18
        # 여행 시작 및 종료 시간 직전 준비시간
        ready_time = 2

        # 추천 명소 개수 담을 변수
        total_place_num = 0
        # sum_time : 만약 여행시간이 30시간 이상일 경우 명소 7개로 추천해주기 위해 선언
        sum_time = 0

        #여행 일 수 계산
        trip_day = end_day - start_day + 1
        print("trip_day",trip_day)

        for i in range(trip_day):
            # 날짜별 여행다닐 수 있는 시간 계산
            print(i+1,"day","==============================================")
            trip_time = 0
            # 첫 날 여행 시간 계산
            if i == 0:
                trip_time = travel_end_time - start_time - ready_time
                sum_time += trip_time
            #마지막 날 여행 시간 계산
            elif i == trip_day-1:
                trip_time = end_time - travel_start_time - ready_time
                sum_time += trip_time
            #이외의 중간 날짜는 9시간 고정
            else:
                trip_time = 9
                sum_time += trip_time
            print("trip_time",trip_time)
            
            
            # 하루 여행 시간 별 관광지 추천 개수 계산
            if trip_time >= 0 and trip_time <= 1:
                total_place_num += 0.5
            elif trip_time > 1 and trip_time <=3:
                total_place_num += 1
            elif trip_time > 3 and trip_time <= 5:
                total_place_num += 1.5
            elif trip_time > 5 and trip_time <= 8:
                total_place_num += 2
            elif trip_time > 8 and trip_time <= 9:
                total_place_num += 2.5
            else:
                pass
            print("total_place_num : ",total_place_num)
            
        # 총 여행 시간이 30시간 이상일때
        if sum_time >= 30:
            total_place_num = 7
        # 명소가 7개 이상 추천됐을때 7개로 고정
        if total_place_num > 7:
            total_place_num = 7
        print("="*40)
        # 총 여행 시간
        print("sum_time : ", sum_time) 
        # 총 추천 명소 개수
        print("total_place_num : ",round(total_place_num))
        #print("trip_time : ",trip_time)
        return total_place_num

if __name__ == "__main__":
    # row 생략 없이 출력
    pd.set_option('display.max_rows', None)
    test_user=["0", "1", "2"]
    a=KeyWordSimilarit(test_user).re_df()
    print(a)
