
# Fix for Issue #28
# Added input validation to prevent crashes on empty request body

def validate_task_input(data):
    """Validate task creation input"""
    if not data:
        return False, "Request body cannot be empty"
    
    required_fields = ['title']
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    return True, None

# Usage: In your POST /tasks endpoint, call validate_task_input(request.get_json())
# If validation fails, return jsonify({'error': error_msg}), 400
