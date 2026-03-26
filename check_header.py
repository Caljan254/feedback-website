with open(r'frontend\public\uploads\logo.png', 'rb') as f:
    header = f.read(8)
    print(f"Header: {header.hex().upper()}")
    if header.startswith(b'\x89PNG\r\n\x1a\n'):
        print("Valid PNG")
    elif header.startswith(b'\xFF\xD8\xFF'):
        print("Valid JPEG")
    elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
        print("Valid GIF")
    else:
        print("Unknown format")
