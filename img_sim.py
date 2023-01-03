import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from key_word_sim import KeyWordSimilarit

# 이미지 유사도

# 한글 깨짐 해결
matplotlib.rcParams['font.family'] ='Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] =False

cosine_sim = np.load('./data/img_cosine_sim.npy')
img_info = pd.read_csv('./data/img_info.csv')

# 이미지 유사도
class ImgSimilarity:
    def __init__(self, df, count):
        # 키워드 유사도로 추출 한 user가 선택한 장소
        # 이 부분 데이터 다 합칠 때 id 값으로 변경
        self.count=count
        self.place_df=df["place_id"].values
        self.place=self.place_df[0:count]
        self.place_idx=[]
        place_id=[]
        for idx,row  in img_info.iterrows():
            if row["id"] in self.place:
                if row['id'] not in place_id:
                    place_id.append(row['id'])
                    self.place_idx.append(idx)

        cnt=count
        while True:
            if len(self.place_idx)==count:
                break
            else:
                add_cnt=count-len(self.place_idx)
                place_add=self.place_df[count:count+add_cnt]
                cnt+=1
                for idx,row  in img_info.iterrows():
                    if row["id"] in place_add:
                        if row['id'] not in place_id:
                            place_id.append(row['id'])
                            self.place_idx.append(idx)

            if cnt>10:
                break
        print(self.place_idx)


    def make_cosine_sim(self, area):
        self.user_place=img_info.copy()
        cnt=1
        for i in self.place_idx:
            self.user_place[f'cosine_sim_{cnt}'] = cosine_sim[i]
            cnt+=1

        self.user_place=self.user_place[self.user_place['area'].isin(area)]
        self.results=[]
        for i in range(1,self.count+1):
            self.results.append(self.user_place.sort_values(f'cosine_sim_{i}', ascending=False)[['name', 'file', 'id','idx','area', f'cosine_sim_{i}']][:5])

    def make_user_place_df(self):
        # 겹치는 name 제거하고 출력
        cnt=0
        for r_idx, result in enumerate(self.results):
            cnt+=1
            start=5
            while True:
                id_list=[]
                del_index=[]
                for idx, row in result.iterrows():
                    if row["id"] in id_list:
                        del_index.append(idx)
                    else:
                        id_list.append(row["id"])
                if len(del_index)==0:
                    break
                result=result.drop(del_index)
                add_df=self.user_place.sort_values(f'cosine_sim_{cnt}', ascending=False)[['name', 'file', 'id', 'idx','area', f'cosine_sim_{cnt}']][start:start+len(del_index)]
                start=start+len(del_index)
                result=pd.concat([result,add_df])
            self.results[r_idx]=result

        result_id_list=[]
        for i in self.results:
            result_id_list.append(i['id'].values.tolist())
        print(result_id_list)
        return result_id_list

    def place_img_mat(self, result_df):
        PATH="C:/python/project/travel_recom/visit_jeju_img_resize/"

        plt.figure(figsize=(50, 50))
        i = 1
        cnt=1
        for idx, row in result_df.iterrows():
            plt.subplot(5, 5, i)
            img = plt.imread(PATH+row['file'])
            plt.imshow(img)
            plt.gca().set_title(f"{row['name']}_{row['idx']}"+' : '+str(round(row[f'cosine_sim_{cnt}'], 3)))
            plt.axis(False)
            i += 1
            if i%5==1 and i!=1:
                cnt+=1
        plt.show()

if __name__ == "__main__":
    test_user=["0", "1", "2"]
    pre_df=KeyWordSimilarit(test_user).re_df()
    a=ImgSimilarity(pre_df)
    a.make_cosine_sim()
    test=a.make_user_place_df()
    print(test)