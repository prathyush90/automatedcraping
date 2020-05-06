class Trie(object):
    def __init__(self, words):
        newwords = []
        for word in words:
            newwords.append(word.lower())
        self.words = newwords

    def levenshtein(self, word1, word2):
        columns = len(word1) + 1
        rows = len(word2) + 1

        # build first row
        currentRow = [0]
        for column in range(1, columns):
            currentRow.append(currentRow[column - 1] + 1)

        for row in range(1, rows):
            previousRow = currentRow
            currentRow = [previousRow[0] + 1]

            for column in range(1, columns):

                insertCost = currentRow[column - 1] + 1
                deleteCost = previousRow[column] + 1

                if word1[column - 1] != word2[row - 1]:
                    replaceCost = previousRow[column - 1] + 1
                else:
                    replaceCost = previousRow[column - 1]

                currentRow.append(min(insertCost, deleteCost, replaceCost))

        return currentRow[-1]

    def search(self, TARGET, probability):
        results = []
        for word in self.words:
            cost = self.levenshtein(TARGET, word)+1
            #prob = (abs(len(TARGET)-cost))/((abs(len(TARGET)-len(word)) + 1)*cost)
            if(cost == 0):
                cost = 0.000001
            prob = 1/cost
            if prob >= probability:
                results.append((word, prob))

        return results
