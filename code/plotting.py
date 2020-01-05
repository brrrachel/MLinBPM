import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"


def occurrence_plotting(occurrences):
    values = sorted(list(occurrences.values()))
    plt.plot(range(len(values)), values)
    plt.xlabel('Activities')
    plt.ylabel('Occurences')
    plt.grid(True)
    plt.savefig('plots/occurences.pdf')
    plt.show()

