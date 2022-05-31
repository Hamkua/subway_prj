# subway_A_star_Algorithm
 
**20171064 함영권, 20201208 김현수**

동적 html, message body에 데이터를 담기 위해 파이썬을 사용하는 대표적인 웹 프레임워크 장고를 사용하였습니다.
[지하철 최단경로 알고리즘 결과](http://hamkua.pythonanywhere.com/)


### 데이터셋을 파이썬 List로 변환
이전 역에서 다음 역까지의 거리, 역명, 역이 속하는 호선에 대한 정보는 [서울 열린데이터 광장](https://data.seoul.go.kr/dataList/OA-12034/F/1/datasetView.do) 에서 제공하는 csv파일을 Python의 pandas 라이브러리를 통해 읽어들인 후, List로 변환하였습니다.
2차원 형태의 파이썬 리스트가 만들어지게 되는데, 구조는 다음과 같습니다.

```
[
	[]
	[['1호선', '소요산', '0', 0.0], ['1호선', '동두천', '0', 2.5], ...
	[['2호선', '성수2', '1:00', 0.8], ['2호선', '뚝섬', '1:30', 1.1], ...
	...
]
```

행번호가 0인 리스트는 역에 대한 정보를 담지 못하게하고, 1호선 = 1번 인덱스로 접근할 수 있도록 하기 위해 행번호 1부터 담도록 합니다. 


### 다음 역 정보를 가지는 Dictionary생성
다음으로, 파이썬의 dictionary를 생성하고, 역명을 키값으로 정방향, 역방향으로 이동할 수 있는 좌표값 리스트를 value로 가지도록 합니다.
정방향은 리스트에서 행 번호가 같을 경우, 열 번호가 1씩 커지는 방향,
역방향은 리스트에서 행 번호가 같을 경우, 열 번호가 -1씩 커지는 방향이라고 가정합니다.
> 예 : 
서울역의 경우, 1호선에도 존재하고, 4호선에도 존재합니다. 좌표값은 각각 1행 34열, 4행 8열을 가집니다.
"서울역"을 키값으로 조회하게 되면, 리턴받는 value는 [[1, 33], [1, 35], [4, 7], [4, 9]]가 됩니다.

### GET방식으로 요청
사용자가 get방식으로 [지하철A*](http://hamkua.pythonanywhere.com/)에 요청을 보내면, 장고는message body에는 이전에 만들어둔 List를 담아 응답하게 됩니다.

![](https://velog.velcdn.com/images/hamkua/post/0c9b9e5c-973e-493d-992e-0376d443568c/image.png)

따라서, html폼에 직접 역명을 입력할 필요가 없습니다.

### POST방식으로 요청

사용자가 post방식으로 [지하철A*](http://hamkua.pythonanywhere.com/)에 요청을 보내면, A*알고리즘을 사용하여 최단 거리를 구하는 알고리즘이 실행되는데, 


### 전체적인 로직 실행을 담당, solve() 작성

``` python
# 순서대로 시작점과 목적지, 리스트, 딕셔너리, 결과를 담을 리스트
def solve(start, end, data, dic, result):
  
    min_value = 10000    #휴리스틱 함수의 리턴값과 비교할 변수
    for l, x, y in dic[start]:    # 시작점에서 이동할 수 있는 경로 리스트를 돌며 좌표값을 구함, l은 호선 번호로 사용하지 않음.
      visited = []    #data리스트와 같은 크기로 모든 값은 0으로 초기화, 방문 여부와, 이전 좌표를 담을 리스트
      for i in range(len(data)):
          visited.append([0]*len(data[i]))
      route = []    #목적지까지 이어지는 경로를 담을 리스트
      
      check(x, y, data, dic, start, end, visited, route)


      route.reverse()    #목적지에 도착한 경우, visited에 저장되어있는 이전 경로들을 append하여 리턴받았으므로, 순서를 반대로 뒤집어준다.
      
      return_value = heuristic(data, dic, route)    #휴리스틱 함수를 실행한 뒤 리턴받는 정수형 변수
      if(return_value != 0):    #리턴받은 값이 0이 아니라면
        if(min_value > return_value):    
          min_value = return_value
          result_index = route

    for index in result_index:
      x = index[0]
      y = index[1]
      result.append(data[x][y])

    return min_value, result

```

### 목적지까지의 경로를 리스트에 담아 반환, check()

``` python
def check(location_x, location_y, data, dic, start, end, visited, route):
  name = data[location_x][location_y][1]
  if(name != end):
    for l, x, y in dic[name]:
      if(visited[x][y] == 0):
        visited[x][y] = [location_x, location_y]
        if(check(x,y,data,dic,start, end,visited,route) == True):
          
          if(data[x][y][1] != start):
            if location_x == x and location_y > y:
              direction = -1    #정방향
            elif location_x == x and location_y < y:
              direction = 1  #역방향
            else:
              direction = 0

            visited[x][y].append(direction)
            
            route.append(visited[x][y])
          return True

  else:
    return True
```


### 휴리스틱함수 heuristic()

``` python
def heuristic(data, dic, route):
    sum_value = 0
    another_line = False
  
    if(len(route) > 1):  
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

    #경로의 길이가 1보다 큰 경우
    elif(len(route) == 1):
      if route[0][2] == -1:
        sum_value += data[route[0][0]][route[0][1]][3]

      elif route[0][2] == 1:
        sum_value += data[route[0][0]][route[0][1] + 1][3]

      else:
        return 0
      
      
    return sum_value
```
