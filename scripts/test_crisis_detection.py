"""
Crisis Detection System Test Suite
Tests the crisis detection functionality for MyBella
"""

from backend.services.crisis_detection import detect_crisis, get_crisis_response, get_all_crisis_resources

def test_crisis_detection():
    """Test various crisis scenarios"""
    
    print("=" * 70)
    print("MYBELLA CRISIS DETECTION SYSTEM - TEST SUITE")
    print("=" * 70)
    print()
    
    # Test cases
    test_cases = [
        {
            'message': 'I want to kill myself',
            'expected_severity': 'high',
            'category': 'Direct suicide ideation'
        },
        {
            'message': 'planning to end my life tonight',
            'expected_severity': 'high',
            'category': 'Suicide planning'
        },
        {
            'message': 'feeling suicidal lately',
            'expected_severity': 'medium',
            'category': 'Suicidal feelings'
        },
        {
            'message': 'I keep cutting myself',
            'expected_severity': 'medium',
            'category': 'Self-harm'
        },
        {
            'message': 'no point in living anymore',
            'expected_severity': 'low',
            'category': 'Hopelessness'
        },
        {
            'message': 'everyone hates me',
            'expected_severity': 'low',
            'category': 'Severe distress'
        },
        {
            'message': "I'm having a great day!",
            'expected_severity': 'none',
            'category': 'Normal message (no crisis)'
        },
        {
            'message': "feeling a bit stressed from work",
            'expected_severity': 'none',
            'category': 'Normal stress (no crisis)'
        }
    ]
    
    # Run tests
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['category']}")
        print(f"Message: \"{test['message']}\"")
        
        is_crisis, severity, matched_keywords = detect_crisis(test['message'])
        
        print(f"✓ Crisis Detected: {is_crisis}")
        print(f"✓ Severity: {severity}")
        
        if matched_keywords:
            print(f"✓ Matched Keywords: {', '.join(matched_keywords[:3])}...")
        
        # Get appropriate response if crisis
        if is_crisis:
            response = get_crisis_response(severity)
            print(f"✓ Response Type: {response['alert_level']}")
            print(f"✓ Show Resources: {response['show_resources']}")
            print(f"✓ Message Preview: {response['message'][:100]}...")
        
        # Check if matches expected
        status = "✅ PASS" if severity == test['expected_severity'] else "❌ FAIL"
        print(f"{status} (Expected: {test['expected_severity']}, Got: {severity})")
        print("-" * 70)
        print()
    
    # Test resources
    print("=" * 70)
    print("CRISIS RESOURCES TEST")
    print("=" * 70)
    resources = get_all_crisis_resources()
    
    print(f"✓ Total Hotlines: {len(resources['hotlines'])}")
    print(f"✓ Online Resources: {len(resources['online_resources'])}")
    print()
    
    print("Available Hotlines:")
    for hotline in resources['hotlines']:
        print(f"  • {hotline['name']}: {hotline['number']}")
    
    print()
    print("=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    test_crisis_detection()
