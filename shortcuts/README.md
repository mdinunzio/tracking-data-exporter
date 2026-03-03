# Apple Shortcuts Setup

The Streaks and Apple Health exporters use a "pickup file" pattern: an Apple Shortcut exports data to a known iCloud Drive location, and the exporter picks it up.

Run these Shortcuts before running `export-data` each week (or set them on a schedule).

## Streaks Export Shortcut

1. Open the **Shortcuts** app on your iPhone
2. Create a new Shortcut named "Export Streaks Data"
3. Steps:
   - **Get All Streaks** (if the Streaks app provides a Shortcuts action)
   - OR: Open Streaks → Share → Export CSV manually, then use a "Save File" action
   - **Save File** to: `iCloud Drive/Shortcuts/Streaks Exports/streaks-YYYY-MM-DD.csv`
     - Use the "Format Date" action to generate the filename with today's date
4. Optional: Set up an **Automation** to run this every Sunday evening

**Note:** The Streaks app's Shortcuts support varies by version. If direct export isn't available, the simplest approach is to manually export from the Streaks app's share sheet and save to the pickup folder.

## Apple Health Export Shortcut

1. Open the **Shortcuts** app on your iPhone
2. Create a new Shortcut named "Export Health Data"
3. Steps:
   - **Find Health Samples** where:
     - Type is "Body Mass" (weight)
     - Start Date is in the last 7 days
   - **Find Health Samples** where:
     - Type is "Step Count"
     - Start Date is in the last 7 days
   - **Find Health Samples** where:
     - Type is "Active Energy Burned"
     - Start Date is in the last 7 days
   - **Find Health Samples** where:
     - Type is "Apple Exercise Time"
     - Start Date is in the last 7 days
   - Combine into a **Text** block formatted as CSV:
     ```
     date,metric,value
     2026-02-24,weight,190.5
     2026-02-24,steps,8432
     ...
     ```
   - **Save File** to: `iCloud Drive/Shortcuts/Health Exports/health-YYYY-MM-DD.csv`
4. Optional: Set up an **Automation** to run this every Sunday evening

## Pickup Directories

Make sure these directories exist in iCloud Drive:
- `Shortcuts/Streaks Exports/`
- `Shortcuts/Health Exports/`

The exporter looks for the most recent file in each directory. File format can be `.csv`, `.json`, or `.txt`.

## Ate Mate

Ate Mate likely doesn't have Shortcuts support. Options:
1. Take a screenshot of your weekly summary and save it to a pickup folder — the LLM can interpret images
2. Skip it — your journal entries likely capture food-related observations
3. Check if the app has added Shortcuts actions in a recent update

## Tips

- You can create a single "Weekly Export" Shortcut that calls both the Streaks and Health export Shortcuts in sequence
- Use the "Run Shortcut" action to chain them together
- Set the combined Shortcut to run every Sunday via Automations
