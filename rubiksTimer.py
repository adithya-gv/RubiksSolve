import sqlite3
import tkinter as tk
import time

global solveTime
solveTime = 0.0
startTime = 0.0
status = True
solveCount = 0
bestTime = 0.0
avgOf5 = 0.0
global five_times
five_times = []


conn = sqlite3.connect('timesdb.sqlite')
cur = conn.cursor()


def createTable():
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Times (
        solveCount INTEGER NOT NULL,
        solveTime REAL
        );
    ''')

def getBestTime():
    if (solveCount > 0):
        best = cur.execute('SELECT solveTime FROM Times ORDER BY solveTime ASC')
        bestValue = best.fetchone()
        return bestValue[0]
    else: 
        return 0.0

def computeAverage():
    times = cur.execute('SELECT solveTime FROM Times ORDER BY solveCount')
    sum = 0.0
    for i in range(0, solveCount):
        sum = sum + times.fetchone()[0]
    average = sum / solveCount
    return round(average, 2)

def printAvgOf5():
    s = "Last Five Times: "
    if (solveCount > 4):
        times = cur.execute('SELECT solveTime FROM Times ORDER BY solveCount DESC LIMIT 5')
        s = s + (str)(times.fetchone()[0])
        for i in range(1, 5):
            s = s + ", " + (str)(times.fetchone()[0])
    return s

def getAvgOf5():
    five_times = []
    if (solveCount > 4):
        times = cur.execute('SELECT solveTime FROM Times ORDER BY solveCount DESC LIMIT 5')
        for i in range(0, 5):
            five_times.append(times.fetchone()[0])
        return calculateAvgOf5(five_times)
    else:
        return 0.0

def calculateAvgOf5(times):
    sum = 0
    for i in times:
        sum = sum + i
    sum = sum - max(times) - min(times)
    return round(sum / 3.0, 2)

def buttonT():
    global status
    if (status):
        status = False
        mainButton['text'] = "Finish Solve"
        solveStatus['text'] = "Solve Started!"
        startT()
    else:
        status = True
        mainButton['text'] = "Start Solve"
        solveStatus['text'] = "Solve Finished!"
        endT(bestTime)

def startT():
    if (solveCount <= 1):
        createTable()
    global startTime
    startTime = time.time()

def endT(bestTime):
    global solveCount
    endTime = time.time()
    solveTime = round((endTime - startTime), 2)
    lastTime['text'] = "Last Solve Time: " + (str)(solveTime)
    cur.execute('''INSERT INTO Times (solveCount, solveTime) VALUES (?, ?)''', (solveCount + 1, solveTime))
    solveCount = solveCount + 1
    conn.commit()
    if (solveTime < bestTime):
        bestTime = solveTime
        bestTimeDisplay['text'] = "Best Solve Time: " + (str)(bestTime)
    if (solveCount == 1):
        bestTime = solveTime
        bestTimeDisplay['text'] = "Best Solve Time: " + (str)(bestTime)
    avgOf5 = getAvgOf5()
    avgOf5Display['text'] = "Average of 5: " + (str)(avgOf5)
    avgDisplay['text'] = "Average: " + (str)(computeAverage())
    lastFiveTimes['text'] = printAvgOf5()

def deleteTable():
    global solveCount
    print("Tables Reset!")
    cur.executescript('''DROP TABLE IF EXISTS Times''')
    conn.commit()
    solveCount = 1

def deleteLast():
    global solveCount
    print("Deleted Last Solve!")
    cur.executescript('''DELETE FROM Times WHERE solveCount = (SELECT MAX(solveCount) FROM Times)''')
    solveCount = solveCount - 1
    conn.commit()
    bestTime = getBestTime()
    bestTimeDisplay['text'] = "Best Solve Time: " + (str)(bestTime)
    avgOf5 = getAvgOf5()
    avgOf5Display['text'] = "Average of 5: " + (str)(avgOf5)
    lastFiveTimes['text'] = printAvgOf5()

def stop():
    solveStatus['text'] = "Saving Data..."
    conn.commit()
    quit()


print("Welcome to the Rubik's Cube Timer!")

createTable()

count = cur.execute('''SELECT COUNT(*) FROM Times''')
countValue = count.fetchone()
solveCount = countValue[0]

bestTime = getBestTime()
avgOf5 = getAvgOf5()

root = tk.Tk()
root.title("Rubik's Cube Timer")

frame = tk.Frame(root, bd=20)
frame.pack()

mainButton = tk.Button(frame, text = "Start Solve", command = buttonT)
deleteButton = tk.Button(frame, text = "Reset Data", command = deleteTable)
deleteSolveButton = tk.Button(frame, text = "Delete Last", command = deleteLast)
quitButton = tk.Button(frame, text = "Quit", command=stop)

solveStatus = tk.Label(frame, text = "Ready to Time!", pady=10)
lastTime = tk.Label(frame, text = "Last Solve Time: " + (str)(solveTime), pady=10)
bestTimeDisplay = tk.Label(frame, text = "Best Solve Time: " + (str)(bestTime), pady=10)
avgDisplay = tk.Label(frame, text = "Average: " + (str)(computeAverage()), pady = 10)
avgOf5Display = tk.Label(frame, text = "Average of 5: " + (str)(avgOf5), pady = 10)
lastFiveTimes = tk.Label(frame, text = printAvgOf5(), pady = 10)

mainButton.grid(row=0, column=0)
deleteButton.grid(row=0, column=2)
deleteSolveButton.grid(row=0, column=4)
quitButton.grid(row=5, column=2)

solveStatus.grid(row=1, column=2)
lastTime.grid(row=2, column=1)
bestTimeDisplay.grid(row=2, column=3)
avgDisplay.grid(row=3, column=1)
avgOf5Display.grid(row=3, column=3)
lastFiveTimes.grid(row=4, column=2)

root.mainloop()