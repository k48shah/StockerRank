# def horner(coeffs, x):
#     acc=0
#     i = 0
#     while i < len(coeffs):
#         c = coeffs[len(coeffs) - 1 -i]
#         acc = acc * x + c
#         print(acc)
#         i = i + 1
#     return acc
#
# print(horner([2], 3))
# print("\n")
# print(horner([1, 2], 3))
# print("\n")
# print(horner([-19, 7, -4, 6], 3))
# print("\n")
# print(horner([-2, -6, 2, 1], 3))

#a)line 3 should be i = 1
#b) Input 2 strings to cause an error state but no failure in the code
#c) The input is not possible since regardless of the


def min_edit_distance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    index2 = 0
    while index2 < len(s2):
        char2 = s2[index2]
        new_distances = [index2 + 1]
        index1 = 0
        while index1 < len(s1):
            char1 = s1[index1]
            is_eq = char1 == char2
            if is_eq:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1],
                                              distances[index1 + 1],
                                              new_distances[-1])))
            index1 += 1
        distances = new_distances
        index2 += 1
    return distances[-1]

print(min_edit_distance("kitten", "sitting"))
print(min_edit_distance("rosettacode", "raisethysword"))