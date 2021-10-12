import random

def generateTxt(rows = 14, columns = 7):
    data = ''
    horizontalWalls = [["ww"] * rows + ['ww'] for i in range(columns + 1)]   
    verticalWalls = [["wp"] * rows + ['ww'] for i in range(columns)]      
    checkedSquares = [[0] * rows + [1] for i in range(columns)] + [[1] * (rows + 1)] # 
    def makeCheckStep(x, y):
        checkedSquares[y][x] = 1
        directions = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        random.shuffle(directions) # перемешка списка
        for (xDirection, yDirection) in directions:
            if checkedSquares[yDirection][xDirection]:
                continue
            if yDirection == y:
                verticalWalls[y][max(x, xDirection)] = 'pp'
            if xDirection == x:
                horizontalWalls[max(y, yDirection)][x] = 'wp'
            makeCheckStep(xDirection, yDirection)
    makeCheckStep(0, 0)


    # сначало horizontalWalls 1 список, потом verticalWalls 1 список и в цикл
    for (horizontalWall, verticalWall) in zip(horizontalWalls, verticalWalls):
        data += ''.join(horizontalWall + ['\n'] + verticalWall + ['\n'])
        
    reversedData = data[::-1]
    data = data + reversedData.lstrip() # удалить пробелы
    data = data[:312] + 'U' + data[312+1:]
    data = data[:35] + '2' + data[35+1:]
    data = data[:82] + '3' + data[82+1:]
    data = data[:117] + '4' + data[117+1:]
    data = data[:38] + '5' + data[38+1:]
    with open("generator.txt", 'w') as txtFile:
        txtFile.write(data)