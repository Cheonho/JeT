from flask import Flask, request, jsonify, Response
from haversine import haversine
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
import pandas as pd
import numpy as np
# MySQLdb는 pymysql.install_as_MySQLdb() 이런식으로 install 해줘야 한다

# 내가 만든 파일
from img_sim import ImgSimilarity
from key_word_sim import KeyWordSimilarit
from user_orientation import UserOrientation
# db 완료 후 db에서 가져오는 코드로 바꿔주기
# df=pd.read_csv("./data/visit_jeju_merge_data_v13.csv", encoding='cp949')

# db 연결
db = pymysql.connect(host="localhost", port=3306, user="root", passwd="mysql", db="JeT", charset="utf8")
cursor=db.cursor()

engine=create_engine("mysql://root:mysql@127.0.0.1/JeT", encoding="utf-8")

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
    user_id=param['userId']
    tendency_result=param["tendency_result"]

    # keyword로 유저의 장소 선호도 생성
    pre_df=KeyWordSimilarit(key_word).re_df()

    # img 유사도
    img_sim=ImgSimilarity(pre_df, 5)
    img_sim.make_cosine_sim()
    place_list=img_sim.make_user_place_df()

    # user 성향에 따라 장소 결정
    # 사용자 성향 값 
    # 0. 유사도 높은 순
    # 1. 최단 거리
    # 2. 인기순위
    # 3. 사람들이 잘 안가는 곳
    
    user=UserOrientation(place_list)
    if tendency_result==0:
        course, distance=user.high_similarity()
    elif tendency_result==1:
        course, distance=user.shortest_distance()
    elif tendency_result==2:
        course, distance=user.popularity_ranking("popularity")
    elif tendency_result==3:
        course, distance=user.popularity_ranking("unpopularity")
    else:
        print("성향이 없음")

    course_dict={}
    course_dict["userId"]=user_id
    for i in range(7):
        if len(course)<=i:
            course_dict[f"place{i+1}"]=np.NaN
        else:
            course_dict[f"place{i+1}"]=course[i]

    course_df=pd.DataFrame([course_dict])
    course_df.to_sql(name="course", con=engine, if_exists="append", index=False)

    response={
        "message":"ok"
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run()