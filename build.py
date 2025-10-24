import PyInstaller.__main__


PyInstaller.__main__.run(
    [
        "core/main.py",
        "--onefile",
        "--windowed",
        "--add-data=assets:assets",  # -- all assets directly in root
        "--add-data=graphics/shaders:graphics/shaders",  # -- all shaders in root
        "--name=cat",
    ]
)
