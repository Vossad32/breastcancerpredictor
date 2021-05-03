
from flask import Flask, render_template
import requests
import json
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, DecimalField

class PredictForm(FlaskForm):
   age = IntegerField('Age (years)')
   bmi = DecimalField('BMI (kg/m2)')
   glucose = IntegerField('Glucose (mg/dL)')
   insulin  = DecimalField('Insulin (µU/mL)')
   homa = DecimalField('HOMA')
   leptin = DecimalField('Leptin (ng/mL)')
   adiponectin = DecimalField('Adiponectin (µg/mL)')
   resistin = DecimalField('Resistin (ng/mL)')
   mcp = DecimalField('MCP-1(pg/dL)')
   submit = SubmitField('Predict')
   abc = "" # this variable is used to send information back to the front page

app = Flask(__name__, instance_relative_config=False)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'development key'

@app.route('/', methods=('GET', 'POST'))

def startApp():
    form = PredictForm()
    return render_template('index.html', form=form)

@app.route('/predict', methods=('GET', 'POST'))
def predict():
    form = PredictForm()

    if form.submit():

        # NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
        API_KEY = "EDq3NYJwnxegkXVHS6xjGwYRJ42lJTSslnuCFoOtLIbH"
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        mltoken = token_response.json()["access_token"]

        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

        # NOTE: manually define and pass the array(s) of values to be scored in the next line
        array_of_input_fields = ["Age", "BMI", "Glucose","Insulin", "HOMA", "Leptin", "Adiponectin", "Resistin", "MCP.1"]
        
        if(form.bmi.data == None):
          python_object = []
        else:
          python_object = [int(form.age.data), float(form.bmi.data), int(form.glucose.data),
            float(form.insulin.data), float(form.homa.data), float(form.leptin.data), float(form.adiponectin.data),
            float(form.resistin.data),float(form.mcp.data)]

        array_of_values_to_be_scored = []
        array_of_values_to_be_scored.extend(python_object)
        payload_scoring = {"input_data": [{"fields": [array_of_input_fields], "values": [array_of_values_to_be_scored]}]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/3505dc73-7c56-473c-af63-62ff3c0d54f6/predictions?version=2021-05-02', json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        print(response_scoring.json())
        output = response_scoring.json()
        for key in output:
          opt = output[key]

        for key in opt[0]:
          bc = opt[0][key]

        roundedResult = round(bc[0][0],2)
        if roundedResult == 2:
          msg = "No potential risk of breast cancer"
        else:
          msg = "Potential risk of breast cancer. Recommended to see a doctor."

        form.outcome = msg
        return render_template('index.html', form=form)

if __name__ == "__main__":
  app.run()