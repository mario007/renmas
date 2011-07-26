
import renmas
import renmas.volume

field = renmas.volume.Field2D(10, 10)

for i in range(10):
    for j in range(10):
        field.write(i, j, 0.44)

field.write_to_file("test.txt")
print(field)

