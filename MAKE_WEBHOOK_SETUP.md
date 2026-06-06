# Make.com Webhook Setup — Connect Google Form to HelpLink

## Google Form URL
https://forms.gle/zESR46gaimxAKEsg9

## HelpLink Webhook URL (production)
https://helplink-backend-production.up.railway.app/api/sos/submit-form

## Local development webhook URL
http://localhost:8000/api/sos/submit-form

## Step-by-step Make.com setup

1. Go to make.com — create a free account
2. Click "Create a new scenario"
3. Click the + button to add a module
4. Search for "Google Forms" — select "Watch Responses"
5. Connect your Google account
6. Select the form: "HelpLink Emergency SOS"
7. Click the + to add a second module
8. Search for "HTTP" — select "Make a request"
9. Configure the HTTP module:
   - URL: https://helplink-backend-production.up.railway.app/api/sos/submit-form
   - Method: POST
   - Body type: Raw
   - Content type: application/json
   - Body:
     ```json
     {
       "name": "{{1.`Your name (optional)`}}",
       "phone": "{{1.`Phone number (optional)`}}",
       "message": "{{1.`Describe your emergency`}}",
       "location": "{{1.`Your location`}}",
       "person_count": "{{1.`How many people need help`}}",
       "language": "{{1.`Language`}}"
     }
     ```

10. Click "Run once" to test
11. Fill the Google Form with test data
12. Check Make.com — it should show the HTTP request succeeded (200 OK)
13. Check HelpLink dashboard — a red SOS marker should appear

## Field name mapping
The field names in the Make.com body must EXACTLY match
the question text in your Google Form. If your form uses
different question text, update the field names above to match.

## Activating the scenario
Click the ON/OFF toggle in Make.com to activate the scenario.
Once active, every form submission triggers HelpLink in real time.

Free tier: 1,000 operations/month — enough for disaster response.

## Verify webhook is live
Open browser or curl:
```
GET https://helplink-backend-production.up.railway.app/api/sos/submit-form
```
Expected response: `{"status":"ok","webhook":"google_form_sos_intake","ready":true}`