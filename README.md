# siwave_ui

This repository contains a graphical user interface for setting up and running SIwave power integrity simulations. The interface is implemented using **PySide6** and helps engineers load layout files, select nets, configure frequency ranges, and start simulations. Results such as S-parameter plots can be viewed and downloaded directly from the application.

Run the application with:

```bash
python main.py
```

When prompted to load a layout, choose the `edb.def` file located inside your
`.aedb` folder. The application will pass the folder to SIwave for import.

The stackup configuration exported by the application is saved as `stack.xml` in the current working directory. Use this file when editing or importing stackup settings.
