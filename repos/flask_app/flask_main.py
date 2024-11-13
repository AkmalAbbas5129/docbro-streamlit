from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to add two numbers
@app.route('/sum', methods=['GET'])
def sum_numbers():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return jsonify({"result": a + b})

# Function to multiply two numbers
@app.route('/multiply', methods=['GET'])
def multiply_numbers():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return jsonify({"result": a * b})

# Function to subtract two numbers
@app.route('/subtract', methods=['GET'])
def subtract_numbers():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return jsonify({"result": a - b})

# Function to divide two numbers
@app.route('/divide', methods=['GET'])
def divide_numbers():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    if b == 0:
        return jsonify({"error": "Division by zero is not allowed."}), 400
    return jsonify({"result": a / b})

# Main function to run the app
if __name__ == '__main__':
    app.run(debug=True)
