# Street Kings TEW9 Enhanced Editor

A PyQt6-based application for enhancing and editing photos for the [Total Extreme Wrestling IX](https://greydogsoftware.com/title/total-extreme-wrestling-ix-2/) game, from [Grey Dog Software](https://www.greydogssoftware.com/) by [Adam Ryland](https://forum.greydogsoftware.com/profile/15-adam-ryland/). This tool is designed to provide an enhanced experience for editing the databases associated for the game. This is specifically designed to help mod makers with creating mods with ease.

## Features

- **Photo Editor**: Edit and manage worker photos for the Street Kings TEW9 game
- **Photo Cache Management**: Efficiently handle both local and game worker photo caches
- **Database Integration**: Connects to the game database to read and update worker information
- **Settings Management**: Comprehensive settings system for application configuration

## Planned Future Features

- **Worker Editor**: Edit wrestler attributes, skills, and statistics
- **Company Editor**: Modify promotion details, finances, and relationships
- **Event Editor**: Create and edit wrestling events, cards, and schedules
- **Contract Editor**: Manage wrestler contracts and terms
- **Title Belt Editor**: Design and configure championship belts
- **Arena Editor**: Create and modify venue configurations
- **Storyline Editor**: Develop and manage wrestling storylines and angles

## Prerequisites

- Windows 10 or higher / macOS 13 or higher / Linux (Ubuntu 22.04 or higher)
- Microsoft Access 2010 or higher / Microsoft Access 2010 Runtime or higher
- Python 3.11.8 or higher
- Additional dependencies listed in `requirements.txt`

### Platform-Specific Requirements

- **Windows Users**: Microsoft Access or the Microsoft Access Runtime is required to access the TEW9 database directly.
- **Mac/Linux Users**: Contact the author for the "SKDBAPI" application, which creates an API bridge to the Access database. Note that this still requires Microsoft Access or Microsoft Access Runtime to be installed on a Windows machine.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/aznironman/sktew9ee
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application using:

```bash
python app.py
```

## Application Structure

- **app.py**: Main application entry point
- **ui/**: User interface components
  - **main_menu.py**: Main application menu
  - **settings_menu.py**: Settings interface
  - **photo_editor/**: Photo editing interface components
- **modules/**: Core functionality modules
  - **photo_editor/**: Photo editing and management functionality
  - **tables/**: Database table definitions and operations
- **database/**: Database connection and operations
  - **sqlite.py**: SQLite database handling
  - **tewdb.py**: TEW game database handling
  - **msaccess.py**: MS Access database support
- **settings/**: Application settings management
- **utils/**: Utility functions and helpers
- **bin/**: Binary and resource files

## Configuration

The application stores settings in a file with the `.sktew9ee` extension. Settings can be configured through the settings menu in the application.

## Development

This application is still in very early development. Functionality is limited to the photo editor and photo cache management.

## License

MIT License

Copyright (c) 2025 Clark & Burke, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Author Contact Information

- **Email**: [streetkings@cnb.llc](mailto:streetkings@cnb.llc)
