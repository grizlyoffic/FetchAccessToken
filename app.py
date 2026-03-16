from flask import Flask, render_template, request, jsonify
import requests
import urllib.parse

app = Flask(__name__)

# होम पेज - index.html रेंडर करेगा
@app.route('/')
def index():
    return render_template('index.html')

# EAT टोकन पेज रेंडर करेगा
@app.route('/eattoken')
def eattoken():
    return render_template('eattoken.html')

# API endpoint - EAT टोकन से डेटा फेच करेगा
@app.route('/api/fetch-eat', methods=['GET', 'POST'])
def fetch_eat():
    try:
        # GET या POST से टोकन लें
        if request.method == 'POST':
            data = request.get_json()
            eat_token = data.get('eat_token', '')
        else:
            eat_token = request.args.get('eat_token', '')
        
        if not eat_token:
            return jsonify({
                'status': 'error',
                'message': 'EAT token is required'
            }), 400
        
        # EAT API को कॉल करें
        api_url = f"https://eat-access.vercel.app/Eat?eat_token={urllib.parse.quote(eat_token)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({
                'status': 'error',
                'message': f'API returned status code: {response.status_code}',
                'details': response.text[:200]
            }), response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'Request timeout - API took too long to respond'
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': 'Connection error - Could not connect to API'
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

# डायरेक्ट EAT फेच के लिए एंडपॉइंट
@app.route('/api/direct-eat', methods=['GET'])
def direct_eat():
    eat_token = request.args.get('token', '')
    if not eat_token:
        return jsonify({
            'status': 'error',
            'message': 'Token parameter required'
        }), 400
    
    # रीडायरेक्ट करें
    return redirect(f"/api/fetch-eat?eat_token={urllib.parse.quote(eat_token)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
