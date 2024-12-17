# spreadsheet_server

This is a project that I completed as a part of my Distributed Systems class while at Notre Dame! It is a basic implementation of the core functionalities of Google Sheets. It follows a client-server architecture, in which multiple clients could connect to my event-driven SpreadSheetServer.py and be able to edit the same spreadsheet in real-time. The 5 main client-side spreadsheet operations are: 

insert( row, col, value ) -> Inserts the given value at a numeric row and column, overriding any existing value.
lookup( row, col ) -> Returns the value stored at that row and column.
remove( row, col ) -> Removes the value from that location.
size() -> Returns the maximum row and column values currently in use.
query( row, col, width, height ) -> Returns a rectangular subset of the spreadsheet.

Clients would send their spreadsheet operation requests via TCP to the server, who would then edit the server's local copy of the spreadsheet. Upon completion of the request, the server would send an acknowledgemenmt.

Moreover, I have also added failure tolerance to my project, ensuring that if the server may fail at any moment in time, it can safely pick up where it left off without any lost information. This has been through logging client operations and checkpointing. Likewise, I have also client robustness and added functinality for the client to not automatically fail once the server disconnects, but keep retrying the server until success. 
