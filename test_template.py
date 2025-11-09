from backend import create_app
import traceback

try:
    app, _ = create_app()
    
    from flask import render_template

    with app.test_request_context('/'):
        try:
            result = render_template('index_nextjs.html')
            print("Template rendered successfully!")
            print(f"Length: {len(result)} characters")
        except Exception as e:
            print(f"Template rendering error: {e}")
            print("Full traceback:")
            traceback.print_exc()
            
except Exception as e:
    print(f"App creation error: {e}")
    traceback.print_exc()