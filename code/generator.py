from random import choice

def replaceSignByIndex(str, index, sign):
    str = str[:index] + f'{sign}' + str[index + 1:]
    return str
    
def generateTxtFile():
    data = ''
    for i in range(900):
        if len(data) % 31 == 0:
            data += '\n'
        else:
            data += 'w'
    data = data.replace('\n', 'w' * 30 + '\n', 1)


    coordsWithoutBorder = []
    for y in range(32, 897, 31):
        for x in range(y, y + 28):
            data = replaceSignByIndex(data, x, 'p')
            coordsWithoutBorder.append(x)
    

    def getRandomCoord():
        return choice(coordsWithoutBorder)

    startRandomCoordinates = []
    for i in range(25):
        startRandomCoordinates.append(getRandomCoord())
        data = replaceSignByIndex(data, startRandomCoordinates[i], 'w')
        if startRandomCoordinates[i] + 1 in coordsWithoutBorder:
            data = replaceSignByIndex(data, startRandomCoordinates[i] + 1, 'w')
            data = replaceSignByIndex(data, startRandomCoordinates[i] - 1, 'w')
            data = replaceSignByIndex(data, startRandomCoordinates[i] - 31, 'w')
            data = replaceSignByIndex(data, startRandomCoordinates[i] + 31, 'w')

    data = replaceSignByIndex(data, 883, 'U')
    data = replaceSignByIndex(data, 71, '2')
    data = replaceSignByIndex(data, 73, '3')
    data = replaceSignByIndex(data, 75, '4')
    data = replaceSignByIndex(data, 78, '5')

    with open("generator.txt", 'w') as txtFile:
            txtFile.write(data)

print(generateTxtFile())
