import PyInstaller.__main__


PyInstaller.__main__.run(
    [
        "core/main.py",
        "--onefile",
        "--windowed",
        "--add-data=assets:assets",  # All assets directly in root
        "--add-data=graphics/shaders:graphics/shaders",  # All shaders in root
        "--name=cat",
    ]
)