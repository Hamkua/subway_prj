from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader
from django.views.generic import ListView, CreateView
from .models import *
import pandas as pd
import os.path


def create_data_list():
    BASE = os.path.dirname(os.path.abspath(__file__))
    data = open(os.path.join(BASE, "subway_data.csv"))

    df = pd.read_csv(data)
    df = df.loc[:, ["선명", "역명", "시간(분)", "거리(km)"]]

    data = [[]]
    for i in range(1, 9):
        line = df.loc[df["선명"] == (str(i) + "호선")]
        data.append(line.values.tolist())
    return data


def create_data_dictionary(data):
    dy = [-1, 1]
    dictionary = {}
    for i in range(1, 9):
        for j in range(len(data[i])):
            name = data[i][j][1]
            if name not in dictionary:
                dictionary[name] = []

            tmp = dictionary[name]
            for k in range(2):
                nj = j + dy[k]
                if (0 <= nj < len(data[i])):
                    tmp.append([data[i][j][0], i, nj])
                    dictionary[name] = tmp

    return dictionary

def indexView(request):
    if request.method == "GET":
        template = loader.get_template("main/index.html")
        data = create_data_list()

        context = {}
        context["data"] = data
        # context["dic"] = dic
        return HttpResponse(template.render(context, request))

    elif request.method == "POST":
        start = request.POST.get("start")
        destination = request.POST.get("destination")

        data = create_data_list()
        dic = create_data_dictionary(data)

        context = {}
        context["answer"] = start + "에서 " + destination + "까지의 최단 이동경로"

        past_distance, result = solve(start, destination, data, dic, [])
        context["past_distance"] = past_distance
        context["result"] = result

        return render(request, "main/data_inject.html", context)


def check(location_x, location_y, data, dic, start, end, visited, route):
    name = data[location_x][location_y][1]
    if (name != end):
        for l, x, y in dic[name]:
            if (visited[x][y] == 0):
                visited[x][y] = [location_x, location_y]

                if (check(x, y, data, dic, start, end, visited, route) == True):
                    if (data[x][y][1] != start):
                        if location_x == x and location_y > y:
                            direction = -1  # 정방향
                        elif location_x == x and location_y < y:
                            direction = 1  # 역방향
                        else:
                            direction = 0

                        visited[x][y].append(direction)
                        route.append(visited[x][y])
                    return True

    else:
        return True


def solve(start, end, data, dic, result):
    min_value = 10000
    for l, x, y in dic[start]:
        visited = []
        for i in range(len(data)):
            visited.append([0] * len(data[i]))
        route = []
        check(x, y, data, dic, start, end, visited, route)

        route.reverse()

        return_value = heuristic(data, route)
        if (return_value != 0):
            if (min_value > return_value):
                min_value = return_value

                result_index = route
        print(min_value)

    for index in result_index:
        x = index[0]
        y = index[1]
        result.append(data[x][y])

    return min_value, result

def heuristic(data, route):
    sum_value = 0
    another_line = False

    if (len(route) > 1):
        for r in route:

            if r[2] == -1:
                sum_value += data[r[0]][r[1] + 1][3]
                if another_line == True:
                    sum_value += data[r[0]][r[1]][3]

            elif r[2] == 1:
                sum_value += data[r[0]][r[1]][3]
                if another_line == True:
                    sum_value += data[r[0]][r[1] - 1][3]

            elif r[2] == 0:
                another_line = True

    # 경로의 길이가 1보다 큰 경우
    elif (len(route) == 1):
        if route[0][2] == -1:
            sum_value += data[route[0][0]][route[0][1]][3]

        elif route[0][2] == 1:
            sum_value += data[route[0][0]][route[0][1] + 1][3]

        else:
            return 0

    return sum_value