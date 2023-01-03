from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from flask_cors import CORS
import json
# MySQLdb는 pymysql.install_as_MySQLdb() 이런식으로 install 해줘야 한다

# 내가 만든 파일
from img_sim import ImgSimilarity
from key_word_sim import KeyWordSimilarit
from user_orientation import UserOrientation
from db import Db

app = Flask(__name__)
CORS(app)

@app.route('/') #test api
def index():
    return 'ok'

@app.route('/tour_course', methods=['POST']) #post echo api
def tour_course():
    # db연결
    db=Db
    engine=db.create_engine()
    conn=engine.connect()
    # post방식으로 넘어온 json data 읽어 들임
    param = request.get_json()
    key_word=param['keyword']
    user_id=param['userId']
    tendency_result=param["tendency_result"]
    area=param["area"]
    start_day = int(param["date_start"].replace("-", ""))
    end_day = int(param["date_end"].replace("-", ""))
    start_time = int(param["duration_start"].split(":")[0])
    end_time = int(param["duration_end"].split(":")[0])

    # keyword로 유저의 장소 선호도 생성
    keyword_place_count=KeyWordSimilarit(key_word, area, tendency_result)
    pre_df=keyword_place_count.re_df()
    place_count=keyword_place_count.day(start_day, end_day, start_time, end_time)

    # img 유사도
    img_sim=ImgSimilarity(pre_df, int(place_count))
    img_sim.make_cosine_sim(area, tendency_result)
    place_list=img_sim.make_user_place_df()

    # user 성향에 따라 장소 결정
    # 사용자 성향 값 
    # 0. 유사도 높은 순
    # 1. 최단 거리
    # 2. 인기순위
    # 3. 사람들이 잘 안가는 곳
    user=UserOrientation(place_list, engine)
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

    print(course)
    # db에 넣는 부분
    course_df=pd.DataFrame([course_dict])

    course_df.to_sql(name="course", con=engine, if_exists="append", index=False)

    course_no = pd.read_sql_query("select courseNo from course order by courseNo desc limit 1;", engine)
    conn.close()
    response={
        "course_no": course_no['courseNo'].tolist()[0],
        "message":"ok"
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run()