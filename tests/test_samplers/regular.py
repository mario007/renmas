
from renmas.samplers import RegularSampler

if __name__ == "__main__":
    regular = RegularSampler(0, 0, 1, 1)

    while True:
        sam = regular.get_sample()
        if sam is None: break
        print (sam)

