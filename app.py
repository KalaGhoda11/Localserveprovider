from flask import Flask, render_template, jsonify, request
import json
import math
from datetime import datetime

app = Flask(__name__)

# Store data in memory
active_requests = []
new_requests_queue = []
accepted_bookings = []  # Store accepted bookings for "My Bookings"
messages_store = []  # Store chat messages

PROVIDERS = [
    {
        "id": 1,
        "name": "John's Electricals",
        "service": "Electrician",
        "rating": 4.8,
        "reviews": 127,
        "lat": 12.9716,
        "lng": 77.5946,
        "price": "₹500-800",
        "phone": "+91 98765 43210",
        "location": "Bangalore, Karnataka",
        "services": ["Installation", "Repair", "Products"]
    },
    {
        "id": 2,
        "name": "QuickFix Plumbing",
        "service": "Plumber",
        "rating": 4.6,
        "reviews": 89,
        "lat": 12.9750,
        "lng": 77.5980,
        "price": "₹400-700",
        "phone": "+91 98765 43211",
        "location": "Bangalore, Karnataka",
        "services": ["Repair", "Installation"]
    },
    {
        "id": 3,
        "name": "SparkPro Electric",
        "service": "Electrician",
        "rating": 4.9,
        "reviews": 203,
        "lat": 12.9700,
        "lng": 77.5900,
        "price": "₹600-1000",
        "phone": "+91 98765 43212",
        "location": "Bangalore, Karnataka",
        "services": ["Installation", "Repair", "Products"]
    },
    {
        "id": 4,
        "name": "HomePro Carpentry",
        "service": "Carpenter",
        "rating": 4.7,
        "reviews": 156,
        "lat": 12.9680,
        "lng": 77.5920,
        "price": "₹800-1500",
        "phone": "+91 98765 43213",
        "location": "Bangalore, Karnataka",
        "services": ["Installation", "Repair", "Products"]
    },
    {
        "id": 5,
        "name": "MasterPlumb Services",
        "service": "Plumber",
        "rating": 4.5,
        "reviews": 78,
        "lat": 12.9730,
        "lng": 77.5960,
        "price": "₹450-750",
        "phone": "+91 98765 43214",
        "location": "Bangalore, Karnataka",
        "services": ["Repair", "Installation"]
    }
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return round(distance, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/consumer/bookings')
def consumer_bookings():
    return render_template('consumer_bookings.html')

@app.route('/api/search')
def api_search():
    service_type = request.args.get('service', '')
    user_lat = float(request.args.get('lat', 12.9716))
    user_lng = float(request.args.get('lng', 77.5946))
    radius = float(request.args.get('radius', 1.0))
    
    results = []
    for provider in PROVIDERS:
        if service_type and provider['service'].lower() != service_type.lower():
            continue
        distance = calculate_distance(user_lat, user_lng, provider['lat'], provider['lng'])
        if distance <= radius:
            provider_copy = provider.copy()
            provider_copy['distance'] = distance
            results.append(provider_copy)
    
    results.sort(key=lambda x: x['distance'])
    return jsonify({
        'providers': results,
        'radius_used': radius,
        'count': len(results)
    })

@app.route('/api/providers')
def get_all_providers():
    return jsonify(PROVIDERS)

@app.route('/api/booking/request', methods=['POST'])
def create_booking_request():
    data = request.json
    
    # Handle broadcast mode
    if data.get('broadcast_mode'):
        # Use a unique ID for the broadcast group
        broadcast_group_id = len(active_requests) + 1
        provider_ids = data.get('provider_ids', [])
        
        # We need a dummy request ID for the consumer to poll, 
        # let's use the broadcast_group_id
        polling_request_id = broadcast_group_id

        for provider_id in provider_ids:
            provider = next((p for p in PROVIDERS if p['id'] == provider_id), None)
            if provider:
                booking_request = {
                    'id': len(active_requests) + 1000 + provider_id, # Ensure unique ID
                    'customer_name': data.get('customer_name'),
                    'provider_id': provider_id,
                    'provider_name': provider['name'],
                    'service_type': data.get('service_type'),
                    'service': provider['service'],
                    'distance': data.get('distance'),
                    'budget': provider['price'],
                    'details': data.get('details'),
                    'customer_phone': data.get('customer_phone'),
                    'customer_lat': data.get('customer_lat'),
                    'customer_lng': data.get('customer_lng'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'time_ago': 'Just now',
                    'status': 'pending',
                    'broadcast_group_id': broadcast_group_id
                }
                active_requests.append(booking_request)
                new_requests_queue.append(booking_request)
        
        return jsonify({
            'success': True,
            'message': f'Broadcast sent to {len(provider_ids)} providers',
            'request_id': polling_request_id # Return the broadcast ID for polling
        })
    else:
        # Single provider booking
        booking_request = {
            'id': len(active_requests) + 1,
            'customer_name': data.get('customer_name'),
            'provider_id': data.get('provider_id'),
            'provider_name': data.get('provider_name'),
            'service_type': data.get('service_type'),
            'service': data.get('service'),
            'distance': data.get('distance'),
            'budget': data.get('budget'),
            'details': data.get('details'),
            'customer_phone': data.get('customer_phone'),
            'customer_lat': data.get('customer_lat'),
            'customer_lng': data.get('customer_lng'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'time_ago': 'Just now',
            'status': 'pending'
        }
        active_requests.append(booking_request)
        new_requests_queue.append(booking_request)
        
        return jsonify({
            'success': True,
            'message': 'Booking request sent',
            'request_id': booking_request['id']
        })

@app.route('/provider/dashboard')
def provider_dashboard():
    return render_template('provider_dashboard.html')

@app.route('/api/provider/requests')
def get_provider_requests():
    # Return all requests (pending and accepted) for filtering on the dashboard
    return jsonify(active_requests)

@app.route('/api/provider/accept-request', methods=['POST'])
def accept_request():
    data = request.json
    request_id = data.get('request_id')
    provider_data = data.get('provider_data', {})
    
    # 1. Find and update the accepted request
    accepted_req = next((req for req in active_requests if req['id'] == request_id), None)
    
    if accepted_req:
        accepted_req['status'] = 'accepted'
        accepted_req['accepted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        accepted_req['provider_details'] = provider_data
        accepted_req['job_status'] = 'accepted'
        accepted_req['payment_status'] = 'unpaid'
        
        # Add to accepted bookings for consumer's "My Bookings"
        accepted_bookings.append(accepted_req.copy())
        
        # 2. If broadcast, reject all other requests in same group
        if 'broadcast_group_id' in accepted_req:
            group_id = accepted_req['broadcast_group_id']
            for other_req in active_requests:
                if (other_req.get('broadcast_group_id') == group_id and 
                    other_req['id'] != request_id and 
                    other_req['status'] == 'pending'):
                    other_req['status'] = 'rejected'
        
        print(f"✅ Request #{request_id} ACCEPTED")
    
    return jsonify({'success': True, 'message': 'Request accepted'})

@app.route('/api/provider/reject-request', methods=['POST'])
def reject_request():
    data = request.json
    request_id = data.get('request_id')
    
    for req in active_requests:
        if req['id'] == request_id:
            req['status'] = 'rejected'
            break
    
    return jsonify({'success': True, 'message': 'Request rejected'})

@app.route('/api/consumer/check-status/<int:request_id>')
def check_request_status(request_id):
    # Check if ANY request in the group was accepted.
    
    # If the request_id is from a single booking (not broadcast), it will have a low ID
    # If the request_id is from a broadcast, it's the broadcast_group_id (a low ID)
    
    # 1. Look for the Broadcast Group ID
    broadcast_group_id = None
    for req in active_requests:
        # Check if any request has this request_id as its broadcast_group_id
        if req.get('broadcast_group_id') == request_id:
            broadcast_group_id = request_id
            break
    
    # 2. If it's not a Broadcast Group ID, it must be a single request ID
    if not broadcast_group_id:
        polled_request = next((req for req in active_requests if req['id'] == request_id), None)
        if not polled_request:
            return jsonify({'status': 'not_found'})
        
        if polled_request['status'] == 'accepted':
            return jsonify({
                'status': 'accepted',
                'provider_details': polled_request.get('provider_details', {})
            })
        
        return jsonify({'status': polled_request['status']})
    
    # 3. Handle Broadcast Group Polling
    if broadcast_group_id:
        accepted_req = next((req for req in active_requests if 
                             req.get('broadcast_group_id') == broadcast_group_id and 
                             req['status'] == 'accepted'), None)
        
        if accepted_req:
            return jsonify({
                'status': 'accepted',
                'provider_details': accepted_req.get('provider_details', {})
            })
    
    # If we are polling a broadcast group ID, and haven't found an accepted request,
    # we return a generic 'pending' status to keep the toast running.
    return jsonify({'status': 'pending'})


@app.route('/api/consumer/my-bookings')
def get_my_bookings():
    # Return only accepted bookings for consumer
    consumer_bookings = [req for req in active_requests if req['status'] == 'accepted']
    return jsonify(consumer_bookings)

@app.route('/api/job/update-status', methods=['POST'])
def update_job_status():
    data = request.json
    request_id = data.get('request_id')
    new_status = data.get('status')
    
    for req in active_requests:
        if req['id'] == request_id:
            req['job_status'] = new_status
            if new_status == 'completed':
                req['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    
    return jsonify({'success': True})

@app.route('/api/payment/process', methods=['POST'])
def process_payment():
    data = request.json
    request_id = data.get('request_id')
    amount = data.get('amount')
    
    for req in active_requests:
        if req['id'] == request_id:
            req['payment_status'] = 'paid'
            req['payment_amount'] = amount
            req['paid_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    
    return jsonify({'success': True})

@app.route('/api/rating/submit', methods=['POST'])
def submit_rating():
    data = request.json
    request_id = data.get('request_id')
    rating = data.get('rating')
    review = data.get('review')
    
    for req in active_requests:
        if req['id'] == request_id:
            req['rating'] = rating
            req['review'] = review
            req['rated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    
    return jsonify({'success': True})

@app.route('/api/messages/<int:request_id>')
def get_messages(request_id):
    msgs = [m for m in messages_store if m['request_id'] == request_id]
    return jsonify(msgs)

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    data = request.json
    message = {
        'id': len(messages_store) + 1,
        'request_id': data.get('request_id'),
        'sender': data.get('sender'),
        'message': data.get('message'),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    messages_store.append(message)
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 LocalServe Server Started!")
    print("="*60)
    print("\n📱 Access URLs:")
    print(f"   Local:     http://127.0.0.1:5000")
    print(f"   Network:   http://YOUR_IP:5000")
    print("\n📋 Pages:")
    print("   Consumer Search:     /search")
    print("   Provider Dashboard:  /provider/dashboard")
    print("   My Bookings:         /consumer/bookings")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)