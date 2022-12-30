from flask import Flask, request, jsonify, Response
import pandas as pd
from haversine import haversine

# 내가 만든 파일
from img_sim import ImgSimilarity
from key_word_sim import KeyWordSimilarit
from user_orientation import UserOrientation
from TSP import TSPAlgorithm
# db 완료 후 db에서 가져오는 코드로 바꿔주기
df=pd.read_csv("./data/visit_jeju_merge_data_v13.csv", encoding='cp949')

app = Flask(__name__)

@app.route('/') #test api
def index():
    return 'ok'

# @app.route('/echo_call/<param>') #get echo api
# def get_echo_call(param):
#     return jsonify({"param": param})

@app.route('/tour_course', methods=['POST']) #post echo api
def tour_course():
    # post방식으로 넘어온 json data 읽어 들임
    param = request.get_json()
    key_word=param['keyword']

    # keyword로 유저의 장소 선호도 생성
    pre_df=KeyWordSimilarit(key_word).re_df()

    # img 유사도
    img_sim=ImgSimilarity(pre_df)
    img_sim.make_cosine_sim()
    place_list=img_sim.make_user_place_df()

    # user 성향에 따라 장소 결정
    tmp_recommendation_list=UserOrientation(place_list).user_tendency('time_sum', min, df)

    # 아마도 최단거리 구하는 코드?
    tsp=TSPAlgorithm(tmp_recommendation_list)

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

    response={
        "place_id":final_recommendation_list[1:-1],
        "message":"ok"
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run()