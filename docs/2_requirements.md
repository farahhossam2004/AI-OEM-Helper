## requirements analysis 
The agent will have the part and the model and the year
first it must identify which one is the part and the model and the year
and see if there is an inavlid input 
so he must ask the user to enter the correct inputs 
after making sure the inputs are valid
it gets the make type
then sends this data to the FAPI catalog 
then gets the response in form of json 
and view it to the car technician

## Functional Requirements 
[ ] Receive the user's request in Arabic or English.
[ ] Extract Make, Model, Year, and Part Name.
[ ] Normalize the part name into the catalog's terminology.
[ ] Validate required fields and input formats.
[ ] Ask the user for missing or ambiguous information.
[ ] Check vehicle and part compatibility through the catalog.
[ ] Send a structured search request to FAPI.
[ ] Validate and interpret the API response.
[ ] Handle no-results, multiple matches, and API failures.
[ ] Retry temporary API failures with a limited retry policy.
[ ] Display verified results and relevant part details.



# Non-Functional Requirements

## 1. Performance
- **NFR-01:** The system shall return a response to the user within 5–10 seconds under normal operating conditions.
- **NFR-02:** The system shall apply a configurable timeout to external API requests to prevent indefinite waiting.

## 2. Accuracy
- **NFR-03:** The system shall only mark OEM part numbers as verified when their compatibility is confirmed by the catalog source.
- **NFR-04:** The system shall clearly label unverified or partially matched results and shall never present them as confirmed OEM matches.
- **NFR-05:** The system shall not generate or assume OEM part numbers using the LLM.

## 3. Usability
- **NFR-06:** The system shall support both Arabic and English user inputs.
- **NFR-07:** The system shall provide clear and understandable responses in the language used by the user whenever possible.
- **NFR-08:** The system shall provide clear validation messages when required vehicle or part information is missing or invalid.

## 4. Reliability
- **NFR-09:** The system shall retry failed external API requests up to two times when the failure is temporary.
- **NFR-10:** If all retry attempts fail, the system shall inform the user that the catalog service is temporarily unavailable and suggest trying again later.
- **NFR-11:** The system shall distinguish between API failures and valid responses containing no matching parts.

## 5. Security
- **NFR-12:** The system shall store API keys and sensitive configuration values in environment variables rather than hardcoding them in source code.
- **NFR-13:** The system shall exclude secrets and environment files from version control.
- **NFR-14:** The system shall avoid exposing API keys or sensitive credentials in application logs and error responses.

## 6. Maintainability
- **NFR-15:** The system shall isolate FAPI integration logic within a dedicated adapter component.
- **NFR-16:** The system shall allow the integration with FAPI to be replaced by another catalog provider without requiring major changes to the Agent's core logic.