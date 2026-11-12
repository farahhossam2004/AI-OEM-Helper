# Task number 101:

Create a new GitHub repo to develop AI Agent to help the car technician find the OEM part number by just input the Make, Model, Year and the part name in Arabic or English, such as -->
The user sends "هوبات كامري 2026".


What you should do:

The Orchestration Workflow
To execute this via a low-code orchestration layer or Telegram bot integration, the workflow requires a three-step reasoning chain:

Intent & Entity Extraction: The user sends "هوبات كامري 2026". The system prompt instructs the primary LLM to extract the entities:
Make: Toyota
Model: Camry
Year: 2026
Component: Front/Rear Brake Rotors (Brake Discs)

Configuration Tool Call: The orchestrator triggers the EPC API tool, passing the extracted parameters. The API handles the regional localization (e.g., defaulting to GCC/Middle East market specs) and resolves the configuration.

Structured Output: The API returns the specific OEM number (e.g., 43512-33140), the required quantity, and any updated supersession numbers. The agent parses this JSON and replies to the user or injects the data directly into a custom ERP DocType for procurement.


Use FAPI Catalog (via MCP): If you are prototyping inside a multi-LLM workspace harness, FAPI acts as a ready-made Model Context Protocol (MCP) server. 
It exposes cross-references and vehicle applicability directly to the AI, allowing it to natively query the auto-parts database without building custom intermediate logic.
