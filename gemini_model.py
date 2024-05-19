import textwrap


import google.generativeai as genai
import json
import xlsxwriter
import os
from dotenv import load_dotenv

from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def get_headings(heading_json):
  all_headings = []
  for heading in heading_json:
    for key in heading.keys():
      if key == "#text" or key == "geographic" or key == "topic" or key == "temporal":
        headings = heading[key]
        if type(headings) == list:
          if len(headings) == 2:
            all_headings.append(headings[0]+"--"+headings[1])
          elif len(headings) == 3:
            all_headings.append(headings[0]+", "+headings[1]+"--"+headings[2])
          else:
            print(headings)
            TypeError("Why is this a list???")
        else:
          all_headings.append(headings)
      elif key == "titleInfo":
        all_headings.append(heading[key]["title"])
      elif key == "name":
        headings = heading[key]["namePart"]
        if type(headings) == list:
          for heading in headings:
            if type(heading) == str:
              all_headings.append(heading)
        else:
          all_headings.append(headings)
  return list(set(all_headings))
      
def format_headings(headings_list):
  headings_string = "1. " +headings_list[0]
  for i in range(1, len(headings_list)):
    headings_string+= "\n"+str(i+1)+". "+headings_list[i]
  return headings_string

def num_correct_predictions(correct_headings, predicted_headings):
  correct_predictions = 0
  for heading in correct_headings:
    if heading.upper() in (name.upper() for name in  predicted_headings):
      correct_predictions+=1
  return correct_predictions

with open('test_data.json') as f:
  test_data= json.load(f)

#Set up Gemini Model
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

#Set up excel worksheet
workbook = xlsxwriter.Workbook('results.xlsx')
worksheet = workbook.add_worksheet()

i = 1
for data in test_data:
  #retrieve book data
  real_headings = get_headings(data["f"])
  num_headings = len(real_headings)
  title = data["t"][0]["title"]
  abstract = None
  if type(data["a"]) == list:
    abstract = data["a"][0]["#text"]
  else:
    abstract = data["a"]["#text"]
  #predict headings using gemini
  predicted_headings_response = model.generate_content("Generate "+str(num_headings)+" Faceted Application of Subject Terminology (FAST) headings for a book with title \""+title+"\" and abstract \""+abstract+"\". Include no other text except the headings and put a newline between each heading (without spaces).")
  predicted_headings = predicted_headings_response.text.split("\n")
  #Calculate and save accuracy
  correct_predictions = num_correct_predictions(real_headings, predicted_headings)
  worksheet.write('A'+str(i), title)
  worksheet.write('B'+str(i), abstract)
  worksheet.write('C'+str(i), format_headings(real_headings))
  worksheet.write('F'+str(i), format_headings(predicted_headings))
  worksheet.write('G'+str(i), correct_predictions/len(real_headings))
  i+=1
workbook.close()

