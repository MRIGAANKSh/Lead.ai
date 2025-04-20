from flask import Flask, request, jsonify, send_file
from lead_generator import generate_leads

app = Flask(__name__)

@app.route('/generate-leads', methods=['POST'])
def generate():
    data = request.json
    business_type = data.get("businessType")
    location = data.get("location")

    if not business_type or not location:
        return jsonify({"success": False, "error": "Missing inputs"}), 400

    generate_leads(business_type, location)
    return jsonify({"success": True, "file": "leads.csv"})

@app.route('/leads.csv')
def download_csv():
    return send_file("leads.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
