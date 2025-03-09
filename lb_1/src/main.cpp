#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>

// Структура описывающая плитку
struct Tile {
    const int rightEdge, bottomEdge;
    int posX, posY, sideLength;

    Tile(int x, int y, int len)
            : posX(x), posY(y), sideLength(len), rightEdge(x + len), bottomEdge(y + len) {}

    Tile(const Tile &other)
            : posX(other.posX), posY(other.posY), sideLength(other.sideLength),
              rightEdge(other.rightEdge), bottomEdge(other.bottomEdge) {}

    Tile &operator=(const Tile &other) {
        if (this != &other) {
            posX = other.posX;
            posY = other.posY;
            sideLength = other.sideLength;
        }
        return *this;
    }
};


int gGridDim;                // нормированная размерность сетки
int gUnitSize;               // единичный размер плитки
int gMinTileCount;           // минимальное количество плиток
std::vector<Tile> gOptimal;  // оптимальное расположение плиток

bool DEBUG_MODE = false;

// Функция нормализации сетки
void adjustGridRatio() {
    int bestDiv = 1;
    for (int d = gGridDim / 2; d >= 1; --d) {
        if (gGridDim % d == 0) {
            bestDiv = d;
            break;
        }
    }
    gUnitSize = bestDiv;
    gGridDim /= bestDiv;
    if (DEBUG_MODE) {
        std::cout << "[DEBUG] adjustGridRatio: bestDiv = " << bestDiv
                  << ", gUnitSize = " << gUnitSize
                  << ", normalized grid dimension = " << gGridDim << std::endl;
    }
}

// Проверка накладывается ли новая плитка на уже размещённые
bool overlapWithTiles(const std::vector<Tile> &tiles, int x, int y) {
    for (const auto &tile : tiles) {
        if (x >= tile.posX && x < tile.rightEdge &&
            y >= tile.posY && y < tile.bottomEdge)
            return true;
    }
    return false;
}

// Определение максимально возможной стороны плитки
int findMaxTileSize(const std::vector<Tile> &tiles, int x, int y) {
    int maxSide = std::min(gGridDim - x, gGridDim - y);
    for (const auto &tile : tiles) {
        if (tile.rightEdge > x && tile.posY > y) {
            maxSide = std::min(maxSide, tile.posY - y);
        } else if (tile.bottomEdge > y && tile.posX > x) {
            maxSide = std::min(maxSide, tile.posX - x);
        }
    }
    return maxSide;
}

void backtrackTiles(std::vector<Tile> &currentTiles, int filledArea, int tileCount, int startX, int startY) {
    if (DEBUG_MODE) {
        std::cout << "[DEBUG] backtrackTiles: tileCount = " << tileCount
                  << ", filledArea = " << filledArea
                  << ", startX = " << startX << ", startY = " << startY << std::endl;
    }
    if (filledArea == gGridDim * gGridDim) {
        if (tileCount < gMinTileCount) {
            gMinTileCount = tileCount;
            gOptimal = currentTiles;
            if (DEBUG_MODE) {
                std::cout << "[DEBUG] Found complete tiling with tileCount = " << tileCount << std::endl;
            }
        }
        return;
    }

    for (int x = startX; x < gGridDim; ++x) {
        for (int y = startY; y < gGridDim; ++y) {
            if (overlapWithTiles(currentTiles, x, y))
                continue;

            int possibleSide = findMaxTileSize(currentTiles, x, y);
            if (possibleSide <= 0)
                continue;

            for (int len = possibleSide; len >= 1; --len) {
                Tile newTile(x, y, len);
                int newFilled = filledArea + len * len;

                int remaining = gGridDim * gGridDim - newFilled;
                if (remaining > 0) {
                    int maxPossible = std::min(gGridDim - x, gGridDim - y);
                    int minNeeded = (remaining + (maxPossible * maxPossible) - 1) / (maxPossible * maxPossible);
                    if (tileCount + 1 + minNeeded >= gMinTileCount)
                        continue;
                }

                if (DEBUG_MODE) {
                    std::cout << "[DEBUG] Placing tile at (" << x << ", " << y
                              << ") with side = " << len
                              << ", newFilled = " << newFilled
                              << ", tileCount = " << tileCount + 1 << std::endl;
                }

                currentTiles.push_back(newTile);
                if (newFilled == gGridDim * gGridDim) {
                    if (tileCount + 1 < gMinTileCount) {
                        gMinTileCount = tileCount + 1;
                        gOptimal = currentTiles;
                        if (DEBUG_MODE) {
                            std::cout << "[DEBUG] Complete tiling reached after placing tile at ("
                                      << x << ", " << y << ") with side = " << len << std::endl;
                        }
                    }
                    currentTiles.pop_back();
                    continue;
                }

                if (tileCount + 1 < gMinTileCount)
                    backtrackTiles(currentTiles, newFilled, tileCount + 1, x, y);
                if (DEBUG_MODE) {
                    std::cout << "[DEBUG] Removing tile at (" << x << ", " << y
                              << ") with side = " << len << std::endl;
                }
                currentTiles.pop_back();
            }
            return;
        }
        startY = 0;
    }
}

// Функция начальной установки плиток с использованием эвристики
void fillTiles() {
    adjustGridRatio();
    int initX = gGridDim / 2;
    int initY = (gGridDim + 1) / 2;
    int areaFilled = initY * initY + 2 * initX * initX;
    std::vector<Tile> initTiles = {
            Tile(0, 0, initY),
            Tile(0, initY, initX),
            Tile(initY, 0, initX)
    };
    if (DEBUG_MODE) {
        std::cout << "[DEBUG] Initial placement:" << std::endl;
        for (const auto &tile : initTiles) {
            std::cout << "[DEBUG] Tile at (" << tile.posX << ", " << tile.posY
                      << ") with side = " << tile.sideLength << std::endl;
        }
        std::cout << "[DEBUG] Initial filled area = " << areaFilled << std::endl;
    }
    backtrackTiles(initTiles, areaFilled, 3, initX, initY);
}

// Вывод оптимального расположения плиток с учетом масштабирования
void printArrangement() {
    std::cout << gMinTileCount << std::endl;
    for (const auto &tile : gOptimal) {
        std::cout << tile.posX * gUnitSize + 1 << " "
                  << tile.posY * gUnitSize + 1 << " "
                  << tile.sideLength * gUnitSize << std::endl;
    }
}

int main() {
    int inputSize;
    std::cin >> inputSize;

    gGridDim = inputSize;
    gMinTileCount = inputSize * inputSize + 1;

    fillTiles();
    printArrangement();
    return 0;
}
