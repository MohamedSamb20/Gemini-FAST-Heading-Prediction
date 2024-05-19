import json

with open('training_data.json') as f:
  training_data= json.load(f)

test_data = []
for i in range(100):
  test_data.append(training_data[i])

training_data = training_data[100:]

with open('test_data.json', 'w') as f:
  json.dump(test_data, f, indent=2)

with open('training_data.json', 'w') as f:
  json.dump(training_data, f, indent=2)