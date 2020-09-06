import numpy as np
import sys

def createDistMatrix(source, target):
    lengthSource = len(source)
    lengthTarget = len(target)

    matrix = np.zeros((lengthTarget + 1, lengthSource + 1), dtype=int)

    for col in range(lengthSource + 1):
        for row in range(lengthTarget + 1):
            if row == 0:
                matrix[row][col] = col
            elif col == 0:
                matrix[row][col] = row
            elif source[col - 1] == target[row - 1]:
                matrix[row][col] = matrix[row - 1][col - 1]
            else:
                insertion = matrix[row - 1][col] + insertion_cost
                deletion = matrix[row][col - 1] + deletion_cost
                substitution = matrix[row - 1][col - 1] \
                    + substitution_cost
                cost = min(insertion, deletion, substitution)
                matrix[row][col] = cost

    return matrix


def CalcOperations(matrix, source, target):
    lengthSource = len(source)
    lengthTarget = len(target)
    
    ptr = []
    steps = []
    (subs, ins, dele) = (0, 0, 0)
    (row, col) = (lengthTarget, lengthSource)
    
    while row >= 0 and col >= 0:
    
        #print(row, col)
        if row > 0 and col > 0:
            value = matrix[row][col]

            if matrix[row - 1][col - 1] == value:
                if source[col - 1] == target[row - 1]:
                    ptr.append('diag')
                    row -= 1
                    col -= 1
                else:
                    up = matrix[row - 1][col]
                    left = matrix[row][col - 1]
                    mini = min(up, left)

                    if mini == up:
                        ptr.append('up')
                        step = 'insert ' + target[row - 1]
                        ins += 1
                        row -= 1
                    else:

                        ptr.append('left')
                        step = 'delete ' + source[col - 1]
                        dele += 1
                        col -= 1
                    steps.append(step)
            else:
                up = matrix[row - 1][col]
                left = matrix[row][col - 1]
                diag = matrix[row - 1][col - 1]
                mini = min(up, left, diag)

                if mini == up:
                    ptr.append('up')
                    step = 'insert ' + target[row - 1]
                    ins += 1
                    row -= 1
                elif mini == left:
                    ptr.append('left')
                    step = 'delete ' + source[col - 1]
                    dele += 1
                    col -= 1
                else:
                    ptr.append('diag')
                    step = 'substitute ' + source[col - 1] + ' with ' \
                        + target[row - 1]
                    subs += 1
                    row -= 1
                    col -= 1
                steps.append(step)
        else:
            if col - 1 < 0:
                ptr.append('up')
                step = 'insert ' + target[row - 1]
                if row != 0:
                    ins += 1
                row -= 1
            elif row - 1 < 0:
                ptr.append('left')
                step = 'delete ' + source[col - 1]
                if col != 0:
                    dele += 1
                col -= 1
            steps.append(step)
    #print(ptr[:-1])
    steps = steps[:-1][::-1]
    return (ins, dele, subs, steps)


if __name__ == "__main__":

    # Defining cost of each operation

    insertion_cost = 1
    deletion_cost = 1
    substitution_cost = 2

    source = sys.argv[1]
    target = sys.argv[2]

    # Making minimum distance matrix

    matrix = createDistMatrix(source, target)
    #print(matrix)
    print("Minimum Edit distance = ", matrix[-1][-1])

    # Calculate number of operations needed

    (ins, dele, subs, steps) = CalcOperations(matrix, source, target)
    print('Insertion: {}, Deletion: {}, Substitution: {}'.format(ins, dele, subs))
    print("Steps: ")
    for step in steps:
        print(step)
