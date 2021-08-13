def getMin(arr, N):
    minInd = 0
    for i in range(1, N):
        if (arr[i] < arr[minInd]):
            minInd = i
    return minInd


def getMax(arr, N):
    maxInd = 0
    for i in range(1, N):
        if (arr[i] > arr[maxInd]):
            maxInd = i
    return maxInd


def minOf2(x, y):
    return x if x < y else y


def minCashFlowRec(amount, N, final_graph):
    mxCredit = getMax(amount, N)
    mxDebit = getMin(amount, N)

    if (amount[mxCredit] == 0 and amount[mxDebit] == 0):
        return 0

    min = minOf2(-amount[mxDebit], amount[mxCredit])
    amount[mxCredit] -= min
    amount[mxDebit] += min

    final_graph[mxDebit][mxCredit] = min

    minCashFlowRec(amount, N, final_graph)


def minCashFlow(graph):
    N = len(graph)
    final_graph = [[0 for i in range(N)] for j in range(N)]

    amount = [0 for i in range(N)]

    for p in range(N):
        for i in range(N):
            amount[p] += (graph[i][p] - graph[p][i])

    minCashFlowRec(amount, N, final_graph)
    return final_graph
