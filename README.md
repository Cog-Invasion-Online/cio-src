# Cog Invasion Online #

Follow these steps to get Cog Invasion Online Dev running on your computer:

* Clone the repository
* Start up the server processes in this order: astron, uberdog, ai (start_astron_server.bat, start_uber_server.bat, start_ai_server.bat)
* Double-click start_ci.bat to run the game (replace account name with whatever)

## How to Clear Your Local Astron Database ##
Sometimes it may be necessary to clear your local Astron database when a change 
has been made to the data that is stored for each avatar or account.

To clear your local Astron database:
* 1) Head to your Astron databases folder (most likely in game/astron/databases).
* 2) Delete 'account-bridge.db'.
* 3) Head to the 'astrondb' directory and delete each numeric file. (ex. 100000000.yaml).
* 4) Reset 'next: ...' inside of 'info.yaml' to 'next: 100000000'.

## Help! The game says my download files are out of date! ##
Usually, when the phase files are updated a new hash is generated. Because of this, you must
update the 'manual_dc_hash' field within your 'astrond.yaml' configuration.

To update the manual dc hash so the game runs:
* 1) Run both Astron and the client and wait until you get the error message stating that your download files are out of date.
* 2) Look inside of your Astron console for the new client hash. Record that new client hash in 'astrond.yaml'.

### Contributing ###
* Commit your changes probably at the end of each day.
* Provide a simple explanation of what you did.