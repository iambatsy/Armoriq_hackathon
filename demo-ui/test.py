import google.generativeai as genai
import sys

def check_gemini_quota(api_key):
    """
    Test if a Gemini API key has exhausted its quota.
    
    Args:
        api_key: Your Gemini API key
        
    Returns:
        dict: Status information about the API key
    """
    try:
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Try to make a minimal API call with the current model name
        model = genai.GenerativeModel('gemini-2.0-flash')  # Updated model name
        response = model.generate_content(
            "Hi",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=1,  # Minimal tokens to reduce usage
            )
        )
        
        return {
            "status": "active",
            "message": "API key is valid and has available quota",
            "test_response": response.text
        }
        
    except Exception as e:
        error_message = str(e).lower()
        
        # Check for quota-related errors
        if "quota" in error_message or "resource_exhausted" in error_message or "429" in error_message:
            return {
                "status": "quota_exhausted",
                "message": "API key has exhausted its quota",
                "error": str(e)
            }
        elif "invalid" in error_message or "api_key" in error_message or "401" in error_message:
            return {
                "status": "invalid",
                "message": "API key is invalid",
                "error": str(e)
            }
        elif "404" in error_message or "not found" in error_message:
            return {
                "status": "error",
                "message": "Model not found - trying alternative model",
                "error": str(e)
            }
        else:
            return {
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e)
            }

if __name__ == "__main__":
    # Replace with your API key or pass as command line argument
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = "AIzaSyClKCX2ZVBziJVw27p1N4-ZxD7yWMWBbGA"
    
    result = check_gemini_quota(api_key)
    
    print(f"\n{'='*50}")
    print(f"Status: {result['status'].upper()}")
    print(f"Message: {result['message']}")
    if 'error' in result:
        print(f"Error Details: {result['error']}")
    print(f"{'='*50}\n")