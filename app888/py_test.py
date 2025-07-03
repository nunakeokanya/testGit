import math
def round_down_to_1000(amount):
  return round(amount / 1000) * 1000

def floor_up_to_1000(amount):
  return math.floor(amount / 1000) * 1000

def ceil_down_to_1000(amount):
  return math.ceil(amount / 1000) *1000

number = 44850
r = round_down_to_1000(number)
f = floor_up_to_1000(number)
c = ceil_down_to_1000(number)

print(f'round_down_to_1000: {r}')
print(f'floor_up_to_1000: {f}')
print(f'round_down_to_1000: {c}')