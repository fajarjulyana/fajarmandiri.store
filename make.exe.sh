pyinstaller --noconsole --onefile --icon=icon.ico \
  --add-data "templates;templates" \
  --add-data "static;static" \
  --add-data "fajarmandiri.db;." \
  --add-data "icon.ico;." \
  --hidden-import=eventlet \
  --hidden-import=eventlet.wsgi \
  --hidden-import=eventlet.green \
  --hidden-import=socketio \
  --hidden-import=engineio \
  app.pyw
