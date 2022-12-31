import pandas as pd
import heapq
from copy import deepcopy
from haversine import haversine
import numpy as np

# TSP 알고리즘
#  - 최단 거리 간선의 정보 확인

class Node:
    bound = 0
    def __init__(self, level: int, path: list):
        self.level = level
        self.path = path


class TSPAlgorithm:
    def __init__(self, tmp_recommendation_list) -> None:
        self.INF = int(1e9) # 무한을 의미하는 값으로 10억을 설정
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

# 다익스트라 알고리즘 (TSP 아님)
class Dijkstra:
    def __init__(self, place_list):
        self.INF = int(1e9) # 무한을 의미하는 값으로 10억을 설정
        self.tmp_places = []
        for i in range(len(place_list)):
            for j in range(len(place_list[i])):
                self.tmp_places.append(place_list[i][j])
        self.tmp_places.insert(0,111111)
        # 노드의 개수, 간선의 개수 입력
        self.n = len(self.tmp_places)
        self.m = self.n * (self.n - 1)
        # 각 노드에 연결되어 있는 노드에 대한 정보를 담는 리스트 만들기
        self.graph = [[] for i in range(self.n + 1)]
        # 최단 거리 테이블을 모두 무한으로 초기화
        self.distance = [self.INF] * (self.n+1)

        self.group_dic = {}
        self.group_num = 0
        for i in range(len(self.tmp_places)):
            if i%len(place_list[0]) == 1:
                self.group_num += 1
            self.group_dic[i] = self.group_num


    def dijkstra(self, start):
        q = []
    
        # 시작 노드로 가기 위한 최단 경로는 0으로 설정하여 큐에 삽입
        heapq.heappush(q, (0, start))
    
        self.distance[start] = 0
    
        while q: # 큐가 비어있지 않다면
            # 가장 최단 거리가 짧은 노드에 대한 정보 꺼내기
            dist, now = heapq.heappop(q)
    
            # 현재 노드가 이미 처리된 적이 있는 노드라면 무시
            if self.distance[now] < dist:
                continue
    
            # 현재 노드와 연결된 다른 인접한 노드들을 확인
            for (node, nodeDist) in self.graph[now]:
                cost = dist + nodeDist
    
                # 현재 노드를 거쳐서, 다른 노드로 이동하는 거리가 더 짧은 경우
                if cost < self.distance[node]:
                    self.distance[node] = cost
                    heapq.heappush(q, (cost, node))