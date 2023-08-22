from flask import Flask, send_from_directory, jsonify, request
import os
import openai
import requests
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_url_path='', static_folder='../frontend/dist')

GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

def geocode(location):
  app.logger.warning('lookup location %s', location)
  endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
  params = {
    'input': location,
    'inputtype': 'textquery',
    'fields': 'formatted_address',
    'key': os.getenv('GOOGLE_MAPS_API_KEY')
  }

  response = requests.get(endpoint_url, params=params)
  if response.status_code == 200:
    result = response.json()
    app.logger.warning('testing warning log %s', result)
    return result["candidates"][0]["formatted_address"]
  else:
    return "Error making request"

@app.route('/')
def serve():
  return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/completions', methods=["POST"])
def completions():
  data = request.get_json()
  app.logger.info("Starting call")
  messages = [{
    "role":
    "system",
    "content":
    """You are a helpful assistant that takes some details about some work that needs to be done and fills out a work ticket so that work can be done.

To do this you take the work details given and you do a few things:
 - You fix any mistakes in them.
 - You make them clearer to read
 - You add details to them like the correct address of the work
 - You add details to the ticket about what tools or parts might be needed
 - You add details to the ticket about the estimated time of completion
 - You add details to the ticket with the managers name and contact information
 - You add details to the ticket about hours of operation 
 - You add details to the ticket about parking at the location
 - You add details to the ticket about access information and contact info
 - You add details to the ticket about what experience or credentials someone doing the work might need"""
  }, {
    "role": "user",
    "content": data.get('query')
  }]

  completion = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=messages,
    functions=[{
      "name": "geocode",
      "description": "Get the address for a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA",
          }
        },
        "required": ["location"],
      },
    }])
  response_message = completion.choices[0].message
  app.logger.info("Response: %s", response_message)

  # Step 2: check if GPT wanted to call a function
  if response_message.get("function_call"):
    # Step 3: call the function
    # Note: the JSON response may not always be valid; be sure to handle errors
    available_functions = {
      "geocode": geocode,
    }  # only one function in this example, but you can have multiple
    function_name = response_message["function_call"]["name"]
    fuction_to_call = available_functions[function_name]
    function_args = json.loads(response_message["function_call"]["arguments"])
    function_response = fuction_to_call(
      location=function_args.get("location"), )

    # Step 4: send the info on the function call and function response to GPT
    messages.append(
      response_message)  # extend conversation with assistant's reply
    messages.append({
      "role": "function",
      "name": function_name,
      "content": function_response,
    })  # extend conversation with function response
    second_response = openai.ChatCompletion.create(
      model="gpt-4-0613",
      messages=messages,
    )  # get a new response from GPT where it can see the function response
    # return second_response

  print("Second Response: %s", second_response)
  return jsonify(message=second_response.choices[0].message)


app.run(host='0.0.0.0', port=81, debug=False)
