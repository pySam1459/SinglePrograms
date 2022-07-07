import pygame
from pickle import load as pkload
from time import sleep
from os import environ
pygame.init()

useLayout = False
layout = "super evil"
boldlines = [[270, 0, 270, 810], [540, 0, 540, 810], [0, 270, 810, 270], [0, 540, 810, 540]]
width, height = 810, 810
environ["SDL_VIDEO_WINDOW_POS"] = "0,30"
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Sudoku")


def text(n, pos, size, col):
    font = pygame.font.SysFont("comicsansms", size)
    surf = font.render(str(n), True, col)
    rect = surf.get_rect()
    rect.center = pos
    screen.blit(surf, rect)


def render(array):
    screen.fill([255, 255, 255])
    for row in array:
        for c in row:
            c.render()

    for li in boldlines:
        pygame.draw.line(screen, [0, 0, 0], li[:2], li[2:], 5)
    pygame.display.update()


def intersect(c1, c2):
    return c1.i == c2.i or c1.j == c2.j or (c1.i//3 == c2.i//3 and c1.j//3 == c2.j//3)


def incommon(c1, c2):
    if c1.pos[0] in c2.pos:
        return c1.pos[0]
    elif c1.pos[1] in c2.pos:
        return c1.pos[1]
    else:
        return 0


def combinations(n, narray):
    if n == 1:
        return [[p] for p in narray]
    else:
        lis = []
        for i, p in enumerate(narray, 1):
            x = combinations(n - 1, narray[i:])
            lis += [[p]+y for y in x]
        return lis


class Cell:
    def __init__(self, n, i, j):
        self.i = i
        self.j = j

        self.n = n
        self.pos = [i for i in range(1, 10, 1) if i != n]
        self.col = [16, 16, 16] if n == 0 else [0, 32, 255]

    def render(self, showPos=True):
        pygame.draw.rect(screen, [0, 0, 0], [self.i*90, self.j*90, 90, 90], 1)
        if self.n == 0:
            if showPos:
                for n in self.pos:
                    b = (n-1) // 3 + 1
                    a = n - (b-1)*3
                    text(n, [int(self.i*90+22.25*a), int(self.j*90+22.25*b)], 20, [16, 16, 16])

        else:
            text(self.n, [self.i*90+45, self.j*90+45], 70, self.col)


if useLayout:
    with open(f"layouts/{layout}.pickle", "rb") as file:
        arr = [[Cell(c, i, j) for i, c in enumerate(row)] for j, row in enumerate(pkload(file))]

else:
    arr = [[Cell(0, i, j) for i in range(9)] for j in range(9)]
    adding = True
    while adding:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if 49 <= event.key <= 57:
                    pos = pygame.mouse.get_pos()
                    arr[pos[1] // 90][pos[0] // 90].n = event.key - 48  # [0, 32, 255]
                    arr[pos[1] // 90][pos[0] // 90].col = [0, 32, 255]

                elif event.key == pygame.K_0 or event.key == pygame.K_BACKSPACE:
                    pos = pygame.mouse.get_pos()
                    arr[pos[1] // 90][pos[0] // 90].n = 0
                    arr[pos[1] // 90][pos[0] // 90].col = [16, 16, 16]

                elif event.key == pygame.K_RETURN:
                    adding = False

        screen.fill([255, 255, 255])
        for j in range(9):
            for i in range(9):
                arr[j][i].render(False)

        pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, [0, 0, 255], [pos[0]//90*90, pos[1]//90*90, 90, 90], 2)

        for line in boldlines:
            pygame.draw.line(screen, [0, 0, 0], line[:2], line[2:], 5)

        pygame.display.update()


step = False
solve = False
found = []
iterations = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                solve = True
            if event.key == pygame.K_RIGHT:
                step = True

    render(arr)
    pygame.display.update()

    if step or solve:
        iterations += 1
        con = True
        step = False

        #######Through each row, col, squ and remove n from each cell pos########
        for row in arr:
            for c in row:
                if c.n == 0:
                    for c2 in row:
                        if c2 != c and c2.n != 0 and c2.n in c.pos: ## [2, 3, 4, 5, 6, 7, 8, 9]
                            c.pos.remove(c2.n)
                            con = False

        for i in range(9):
            for row in arr:
                if row[i].n == 0:
                    for row2 in arr:
                        if row2[i] != row[i] and row2[i].n != 0 and row2[i].n in row[i].pos:
                            row[i].pos.remove(row2[i].n)
                            con = False

        for k in range(3):
            for l in range(3):

                for j in range(k*3, (k+1)*3):
                    for i in range(l*3, (l+1)*3):
                        if arr[j][i].n == 0:
                            for j2 in range(k*3, (k+1)*3):
                                for i2 in range(l*3, (l+1)*3):
                                    if arr[j2][i2] != arr[j][i] and arr[j2][i2].n != 0 and arr[j2][i2].n in arr[j][i].pos:
                                        arr[j][i].pos.remove(arr[j2][i2].n)
                                        con = False

        #######if only 1 possible left, n = pos[0]#####
        data = {k: 0 for k in range(1, 10)}
        for row in arr:
            for c in row:
                if c.n == 0 and len(c.pos) == 1:
                    c.n = c.pos[0]
                    con = False
                if c.n != 0:
                    data[c.n] += 1
        for k in range(1, 10):
            if data[k] == 9 and k not in found:
                found.append(k)

        if not con:  ######## for earch row, col, squ, if the a cell contains a unique possibility, then it is that n
            continue

        for row in arr:
            data = {}
            for c in row:
                if c.n == 0:
                    for x in c.pos:
                        if x in data:
                            data[x].append(c)
                        else:
                            data.update({x: [c]})

            for key, value in data.items():
                if len(value) == 1:
                    value[0].n = key
                    con = False

        if not con:
            continue

        for i in range(9):
            data = {}
            for row in arr:
                if row[i].n == 0:
                    for x in row[i].pos:
                        if x in data:
                            data[x].append(row[i])
                        else:
                            data.update({x: [row[i]]})

            for key, value in data.items():
                if len(value) == 1:
                    value[0].n = key
                    con = False

        if not con:
            continue

        for k in range(3):
            for l in range(3):
                data = {}
                for j in range(k*3, (k+1)*3):
                    for i in range(l*3, (l+1)*3):
                        if arr[j][i].n == 0:
                            for x in arr[j][i].pos:
                                if x in data:
                                    data[x].append(arr[j][i])
                                else:
                                    data.update({x: [arr[j][i]]})

                for key, value in data.items():
                    if len(value) == 1:
                        value[0].n = key
                        con = False

        if not con:
            continue

        for p in range(1, 10):
            if p not in found:
                for k in range(3):
                    for l in range(3):
                        data = []
                        match = True
                        for j in range(k*3, (k+1)*3):
                            for i in range(l*3, (l+1)*3):
                                if arr[j][i].n == 0 and p in arr[j][i].pos:
                                    if len(data) == 0:
                                        data.append(arr[j][i])
                                    elif len(data) == 1:
                                        if data[0].i == arr[j][i].i or data[0].j == arr[j][i].j:
                                            data.append(arr[j][i])
                                        else:
                                            match = False
                                    elif len(data) == 2:
                                        if data[0].i == data[1].i == arr[j][i].i:
                                            data.append(arr[j][i])
                                        elif data[0].j == data[1].j == arr[j][i].j:
                                            data.append(arr[j][i])
                                        else:
                                            match = False

                                    else:
                                        match = False

                        if (len(data) == 2 or len(data) == 3) and match:
                            if data[0].i == data[1].i:
                                 for j in range(9):
                                     if arr[j][data[0].i] not in data and p in arr[j][data[0].i].pos and arr[j][data[0].i].n == 0:
                                         arr[j][data[0].i].pos.remove(p)
                                         con = False

                            elif data[0].j == data[1].j:
                                for c in arr[data[0].j]:
                                    if c not in data and p in c.pos and c.n == 0:
                                        c.pos.remove(p)
                                        con = False

        if not con:
            continue

        for row in arr:   #### naked triples
            memo = []
            for c in row:
                if c.n == 0 and c not in memo:
                    data = c.pos[:]
                    for cell in row:
                        if cell.n == 0 and c != cell:
                            for p in cell.pos:
                                if p not in data:
                                    data.append(p)
                            if len(data) > 3:
                                data = c.pos[:]
                                continue
                            d = data[:]
                            for cell2 in row:
                                if cell2.n == 0 and c != cell2 and cell != cell2:
                                    for p in cell2.pos:
                                        if p not in data:
                                            data.append(p)
                                    if len(data) > 3:
                                        data = d[:]
                                        continue
                                    elif len(data) == 3:
                                        for arc in row:
                                            if arc.n == 0 and arc != c and arc != cell and arc != cell2:
                                                for p in data:
                                                    if p in arc.pos:
                                                        arc.pos.remove(p)
                                                        con = False
                                        memo += [c, cell, cell2]

        for i in range(9):
            memo = []
            for row in arr:
                if row[i].n == 0 and row[i] not in memo:
                    data = row[i].pos[:]
                    for r in arr:
                        if r[i].n == 0 and r[i] != row[i]:
                            for p in r[i].pos:
                                if p not in data:
                                    data.append(p)
                            if len(data) > 3:
                                data = row[i].pos[:]
                                continue
                            d = data[:]
                            for r2 in arr:
                                if r2[i].n == 0 and row[i] != r2[i] and r[i] != r2[i]:
                                    for p in r2[i].pos:
                                        if p not in data:
                                            data.append(p)
                                    if len(data) > 3:
                                        data = d[:]
                                        continue
                                    elif len(data) == 3:
                                        for arc in arr:
                                            if arc[i].n == 0 and arc[i] != row[i] and arc[i] != r[i] and arc[i] != r2[i]:
                                                for p in data:
                                                    if p in arc[i].pos:
                                                        arc[i].pos.remove(p)
                                                        con = False
                                        memo += [row[i], r[i], r2[i]]
        for k in range(3):
            for l in range(3):
                memo = []
                for j in range(k*3, (k+1)*3):
                    for i in range(l*3, (l+1)*3):
                        if arr[j][i].n == 0 and arr[j][i] not in memo:
                            data = arr[j][i].pos[:]
                            for b in range(k*3, (k+1)*3):
                                for a in range(l*3, (l+1)*3):
                                    if arr[b][a].n == 0 and arr[b][a] != arr[j][i]:
                                        for p in arr[b][a].pos:
                                            if p not in data:
                                                data.append(p)
                                        if len(data) > 3:
                                            data = arr[j][i].pos[:]
                                            continue
                                        da = data[:]
                                        for d in range(k*3, (k+1)*3):
                                            for c in range(l*3, (l+1)*3):
                                                if arr[d][c].n == 0 and arr[j][i] != arr[d][c] and arr[b][a] != arr[d][c]:
                                                    for p in arr[d][c].pos:
                                                        if p not in data:
                                                            data.append(p)
                                                    if len(data) > 3:
                                                        data = da[:]
                                                        continue
                                                    elif len(data) == 3:
                                                        for jrc in range(k*3, (k+1)*3):
                                                            for irc in range(l*3, (l+1)*3):
                                                                if arr[jrc][irc].n == 0 and arr[jrc][irc] != arr[j][i] and arr[jrc][irc] != arr[b][a] and arr[jrc][irc] != arr[d][c]:
                                                                    for p in data:
                                                                        if p in arr[jrc][irc].pos:
                                                                            arr[jrc][irc].pos.remove(p)
                                                                            con = False
                                                        memo += [arr[j][i], arr[b][a], arr[d][c]]

        if not con:
            continue

        #### hidden pairs, triples, quads, ...
        for row in arr:
            data = []
            length = 0
            for c in row:
                if c.n == 0:
                    length += 1
                    for p in c.pos:
                        if p not in data:
                            data.append(p)
            if length > 2:
                for n in range(2, length):
                    combins = combinations(n, data)
                    for combs in combins:
                        d = []
                        count = 0
                        for c in row:
                            if c.n == 0:
                                allow = True

                                for p in combs:
                                    if p not in c.pos:
                                        allow = False
                                    else:
                                        count += 1
                                if allow:
                                    d.append(c)
                        if len(d) == n and count == n*n:
                            for c in row:
                                if c.n == 0:
                                    if c in d:
                                        if c.pos != combs:
                                            c.pos = combs[:]
                                            con = False
                                    else:
                                        for p in combs:
                                            if p in c.pos:
                                                c.pos.remove(p)
                                                con = False

        for i in range(9):
            data = []
            length = 0
            for row in arr:
                if row[i].n == 0:
                    length += 1
                    for p in row[i].pos:
                        if p not in data:
                            data.append(p)
            if length > 2:
                for n in range(2, length):
                    combins = combinations(n, data)
                    for combs in combins:
                        d = []
                        count = 0
                        for row in arr:
                            if row[i].n == 0:
                                allow = True
                                for p in combs:
                                    if p not in row[i].pos:
                                        allow = False
                                    else:
                                        count += 1
                                if allow:
                                    d.append(row[i])
                        if len(d) == n and count == n*n:
                            for row in arr:
                                if row[i].n == 0:
                                    if row[i] in d:
                                        if row[i].pos != combs:
                                            row[i].pos = combs[:]
                                            con = False

                                    else:
                                        for p in combs:
                                            if p in row[i].pos:
                                                row[i].pos.remove(p)
                                                con = False

        for k in range(3):
            for l in range(3):
                data = []
                length = 0
                for j in range(k*3, (k+1)*3):
                    for i in range(l*3, (l+1)*3):
                        if arr[j][i].n == 0:
                            length += 1
                            for p in arr[j][i].pos:
                                if p not in data:
                                    data.append(p)
                if length > 2:
                    for n in range(2, length):
                        combins = combinations(n, data)
                        for combs in combins:
                            d = []
                            count = 0
                            for j in range(k*3, (k+1)*3):
                                for i in range(l*3, (l+1)*3):
                                    if arr[j][i].n == 0:
                                        allow = True
                                        for p in combs:
                                            if p not in arr[j][i].pos:
                                                allow = False
                                            else:
                                                count += 1
                                        if allow:
                                            d.append(arr[j][i])
                            if len(d) == n and count == n*n:
                                for j in range(k*3, (k+1)*3):
                                    for i in range(l*3, (l+1)*3):
                                        if arr[j][i].n == 0:
                                            if arr[j][i] in d:
                                                if arr[j][i].pos != combs:
                                                    arr[j][i].pos = combs[:]
                                                    con = False
                                            else:
                                                for p in combs:
                                                    if p in arr[j][i].pos:
                                                        arr[j][i].pos.remove(p)
                                                        con = False


        if not con:
            continue

        for p in range(1, 10):   #### X wing
            if p not in found:
                array = []
                datai = {k: 0 for k in range(9)}
                dataj = {k: 0 for k in range(9)}
                for row in arr:
                    array.append([])
                    for c in row:
                        if c.n == 0 and p in c.pos:
                            array[-1].append(c)
                            datai[c.i] += 1
                            dataj[c.j] += 1
                        else:
                            array[-1].append(None)

                for i in range(9):
                    for j in range(9):
                        if array[j][i] is not None:
                            allow = True
                            pair = [array[j][i]]
                            for k in range(j+1, 9):
                                if array[k][i] is not None:   ## pair = [i, j]   [i, k]
                                    if len(pair) == 2:
                                        allow = False
                                        break
                                    elif len(pair) == 1:
                                        pair.append(array[k][i])

                            if allow and len(pair) == 2 and datai[i] == 2:
                                k = pair[1].j
                                for l in range(i+1, 9):
                                    if array[j][l] is not None and array[k][l] is not None:
                                        allow = True
                                        pair2 = [array[j][l], array[k][l]]
                                        for row in array:
                                            if row[l] not in pair2 and row[l] is not None:
                                                allow = False

                                        if allow:
                                            for b in [j, k]:
                                                for a in range(9):
                                                    if a != i and a != l:
                                                        if p in arr[b][a].pos and arr[b][a].n == 0:
                                                            arr[b][a].pos.remove(p)
                                                            array[b][a] = None
                                                            con = False

                            allow = True
                            pair = [array[j][i]]
                            for l in range(i+1, 9):
                                if array[j][l] is not None:
                                    if len(pair) == 2:
                                        allow = False
                                        break
                                    elif len(pair) == 1:
                                        pair.append(array[j][l])

                            if allow and len(pair) == 2 and dataj[j] == 2:
                                l = pair[1].i
                                for k in range(j+1, 9):
                                    if array[k][i] is not None and array[k][l] is not None:
                                        allow = True
                                        pair2 = [array[k][i], array[k][l]]
                                        for io in range(9):
                                            if array[k][io] not in pair2 and array[k][io] is not None:
                                                allow = False
                                        if allow:
                                            for a in [i, l]:
                                                for b in range(9):
                                                    if b != j and b != k:
                                                        if p in arr[b][a].pos and arr[b][a].n == 0:
                                                            arr[b][a].pos.remove(p)
                                                            array[b][a] = None
                                                            con = False

        if not con:
            continue

        for row in arr:    ##### XY wing
            for c in row:
                if c.n == 0 and len(c.pos) == 2:
                    pairing = []
                    commoning = []
                    common = 0
                    for i in range(9):
                        if arr[c.j][i] != c and arr[c.j][i].n == 0 and len(arr[c.j][i].pos) == 2 and arr[c.j][i].pos != c.pos:
                            common = incommon(c, arr[c.j][i])
                            if common != 0:
                                pairing.append(arr[c.j][i])
                                commoning.append(common)
                                common = 0

                    for j in range(9):
                        if arr[j][c.i] != c and arr[j][c.i].n == 0 and len(arr[j][c.i].pos) == 2 and arr[j][c.i].pos != c.pos:
                            common = incommon(c, arr[j][c.i])
                            if common != 0:
                                pairing.append(arr[j][c.i])
                                commoning.append(common)
                                common = 0

                    for j in range((c.j//3)*3, (c.j//3 +1)*3):
                        for i in range((c.i//3)*3, (c.i//3 +1)*3):
                            if arr[j][i] != c and arr[j][i].n == 0 and len(arr[j][i].pos) == 2 and arr[j][i].pos != c.pos:
                                common = incommon(c, arr[j][i])
                                if common != 0:
                                    pairing.append(arr[j][i])
                                    commoning.append(common)
                                    common = 0

                    if len(commoning) != 0 and len(pairing) != 0:
                        for pr, common in zip(pairing, commoning):
                            pair = [c, pr]
                            uncommon = [x for x in c.pos + pr.pos if x != common]
                            triple = None
                            know = []
                            for j in range(9):
                                for i in range(9):
                                    if arr[j][i].n == 0 and len(arr[j][i].pos) == 2 and arr[j][i] not in pair and arr[j][i].pos == uncommon:
                                        allow = False
                                        for cell in pair:
                                            if intersect(arr[j][i], cell):
                                                know = [arr[j][i], cell]
                                                allow = not allow
                                        if allow:
                                            triple = pair + [arr[j][i]]
                                            break
                                if triple is not None:
                                    break

                            if triple is not None:
                                middle = None
                                for cell in triple:
                                    if cell not in know and middle is None:
                                        for cell2 in know:
                                            if intersect(cell, cell2):
                                                middle = cell2
                                                break
                                unknown = 0
                                for x in pair[0].pos + pair[1].pos:
                                    if x not in middle.pos:
                                        unknown = x
                                        break
                                othrs = [cell for cell in triple if cell != middle]
                                for j in range(9):
                                    for i in range(9):
                                        if arr[j][i].n == 0 and unknown in arr[j][i].pos:
                                            remove = True
                                            for cell in othrs:
                                                if not intersect(cell, arr[j][i]):
                                                    remove = False
                                            if remove:
                                                arr[j][i].pos.remove(unknown)
                                                con = False

        if not con:
            continue

        for p in range(1, 10):  ##### swordfish
            if p not in found:
                datai = {k: [] for k in range(9)}
                dataj = {k: [] for k in range(9)}
                array = []
                for j, row in enumerate(arr):
                    array.append([])
                    for i, c in enumerate(row):
                        if c.n == 0 and p in c.pos:
                            datai[i].append(c)
                            dataj[j].append(c)
                            array[-1].append(c)
                        else:
                            array[-1].append(None)

                for j in range(9):
                    if len(dataj[j]) == 2:
                        rows = [dataj[j]]
                        for k in range(j + 1, 9):
                            if len(dataj[k]) == 2:
                                if dataj[j][0].i == dataj[k][0].i and dataj[j][1].i == dataj[k][1].i:
                                    break
                                elif dataj[j][0].i == dataj[k][0].i or dataj[j][0].i == dataj[k][1].i:
                                    rows.append(dataj[k])
                                else:
                                    break
                        else:
                            if len(rows) == 3:
                                if rows[1][0].i == rows[2][0].i and rows[1][1].i == rows[2][1].i:
                                    for i in [rows[0][0].i, rows[0][1].i, rows[2][1].i]:
                                        for k in range(9):
                                            if arr[k][i].n == 0 and p in arr[k][i].pos and k not in [rows[0][0].j, rows[1][0].j,
                                                                                                     rows[2][0].j]:
                                                arr[k][i].pos.remove(p)
                                                con = False

                for i in range(9):
                    if len(datai[i]) == 2:
                        cols = [datai[i]]
                        for l in range(i + 1, 9):
                            if len(datai[l]) == 2:
                                if datai[i][0].j == datai[l][0].j and datai[i][1].j == datai[l][1].j:
                                    break
                                elif datai[i][0].j == datai[l][0].j or datai[i][1].j == datai[l][1].j:
                                    cols.append(datai[l])
                                else:
                                    break
                        else:
                            if len(cols) == 3:
                                if cols[1][0].j == cols[2][0].j and cols[1][1].j == cols[2][1].j:
                                    for j in [cols[0][0].j, cols[0][1].j, cols[2][1].j]:
                                        for l in range(9):
                                            if arr[j][l].n == 0 and p in arr[j][l].pos and l not in [cols[0][0].i, cols[1][0].i,
                                                                                                     cols[2][0].i]:
                                                arr[j][l].pos.remove(p)
                                                con = False

        if not con:
            continue

        solved = True   ####### check if the sudoku is solved
        for row in arr:
            for c in row:
                if c.n == 0:
                    solved = False


        if not solved and con: ##### if can't continue
            break


render(arr)
pygame.display.update()
# print(f"Total Iterations {iterations}")
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

