from flask import Flask, request, jsonify
from flask_cors import CORS
from solver.vrp_solver import solve_vrp

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS สำหรับทุก endpoint

@app.route('/solve', methods=['POST'])
def solve():
    data = request.get_json(force=True)
    result = solve_vrp(data)
    if result is None:
        return jsonify({"error": "No solution found"}), 400
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
