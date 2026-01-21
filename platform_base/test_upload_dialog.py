#!/usr/bin/env python3
"""
Teste simples para o UploadDialog e verificação do preview
"""

import sys
sys.path.insert(0, 'src')

from PyQt6.QtWidgets import QApplication
from platform_base.desktop.session_state import SessionState
from platform_base.desktop.signal_hub import SignalHub
from platform_base.desktop.dialogs.upload_dialog import UploadDialog

def test_upload_dialog():
    """Teste básico do UploadDialog"""
    app = QApplication(sys.argv)
    
    # Create session components
    signal_hub = SignalHub()
    session_state = SessionState("test_session", signal_hub)
    
    # Create dialog
    dialog = UploadDialog(session_state, signal_hub)
    
    # Set test file path (usando arquivo XLSX da raiz)
    test_file = "../BAR_FT-OP10.xlsx"
    dialog.file_path_edit.setText(test_file)
    dialog._on_file_path_changed(test_file)
    
    # Show dialog
    dialog.show()
    
    print("Dialog criado com sucesso!")
    print(f"Arquivo teste: {test_file}")
    print(f"Formato detectado: {dialog.format_label.text()}")
    print(f"Botões habilitados - Preview: {dialog.preview_btn.isEnabled()}, Load: {dialog.load_btn.isEnabled()}")
    
    # Don't run event loop for testing
    # app.exec()

if __name__ == "__main__":
    test_upload_dialog()