# ProteinBot

This project uses Watson Speech to Text, Conversation, and Text to Speech services to provide information about proteins. Experimental. Uses protein names from UniProt to create a custom corpus for speech recognition.

Copy `myconfig.sample.py` to `myconfig.py` and provide username and passwords for the various Watson services.

# Intents
Information about protein structures from PDB for a specified protein name. Optionally, the structures could be limited to one of these identification methods: x-ray crystallography, solution NMR, electron microscopy:
- `#structure-exists` If any structures are available for that particular protein (Y/N)
- `#structure-count` Number of structures available for a protein

Ligands information from PDB:
- `#ligand-count` Number of ligands associated with proteins in context
- `#ligand-names` Names of ligands associated with proteins in context

Other structure information from PDB about the proteins in context:
- `#structure-titles` Get the structure titles
- `#release-dates` Structure release dates
- `#citation-dates` Citations by year
- `#show-details` Show detailed info on a browser

Utilities:
- `#set-method` Set the structure identification method
- `#forget-method` Clear the structure identification method
- `#end-conversation` End the session

# Reference websites:
1. RCSB Protein Data Bank (PDB): http://www.rcsb.org/
1. UniProt KB: http://www.uniprot.org/
