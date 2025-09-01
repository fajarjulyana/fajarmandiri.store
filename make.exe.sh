pyinstaller --noconsole --onefile --icon=icon.ico \
  --add-data "templates;templates" \
  --add-data "static;static" \
  --add-data "fajarmandiri.db;." \
  --add-data "icon.ico;." \
  app.pyw
