import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 1, 3, 6, 7]

cluster = ['^', '^', '^', 's', 's']

fig, ax = plt.subplots()

for xp, yp, m in zip(x, y, cluster):
    ax.scatter([xp],[yp], marker=m)
pass

plt.show()