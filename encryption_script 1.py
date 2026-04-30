import os
import sys
import base64
import marshal
import types
from cryptography.fernet import Fernet

def generate_key():
    """Generate a new encryption key"""
    return Fernet.generate_key()

def compress_and_encrypt_file(file_path, key=None):
    """
    Compress and encrypt a Python file while keeping it executable
    """
    # if key is None:
    #     key = generate_key()
    key = b'VgBfmQrBDFXUzYfAJ2rEipY43_AaKuG3RHS7ntapDj0='

    fernet = Fernet(key)
    
    
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    
    compiled_code = compile(source_code, file_path, 'exec')
    
    
    marshaled_code = marshal.dumps(compiled_code)
    
    
    encrypted_code = fernet.encrypt(marshaled_code)
    
    
    encoded_encrypted_code = base64.b64encode(encrypted_code).decode('utf-8')
    
    
    wrapper_template = f'''
import base64
import marshal
import types
from cryptography.fernet import Fernet

def _decrypt_and_execute():
    key = {key!r}
    fernet = Fernet(key)
    
    encrypted_data = base64.b64decode({encoded_encrypted_code!r})
    decrypted_data = fernet.decrypt(encrypted_data)
    
    code_object = marshal.loads(decrypted_data)
    exec(code_object, globals())

if __name__ == "__main__":
    _decrypt_and_execute()
else:
    # For imports, execute immediately
    _decrypt_and_execute()
'''
    
    return wrapper_template, key

def compress_file(input_file, output_file=None, key=None):
    """
    Compress a Python file and save the encrypted version
    """
    if output_file is None:
        name, ext = os.path.splitext(input_file)
        output_file = f"{name}_compressed{ext}"
    
    try:
        compressed_code, encryption_key = compress_and_encrypt_file(input_file, key)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(compressed_code)
        
        print(f"✓ Successfully compressed: {input_file} -> {output_file}")
        print(f"✓ Encryption key: {encryption_key.decode()}")
        
        return output_file, encryption_key
        
    except Exception as e:
        print(f"✗ Error compressing {input_file}: {str(e)}")
        return None, None

def compress_directory(directory_path, key=None):
    """
    Compress all Python files in a directory
    """
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory")
        return
    
    python_files = []
    for root, dirs, files in os.walk(directory_path):
        
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py') and not file.endswith('_compressed.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print("No Python files found to compress")
        return
    
    print(f"Found {len(python_files)} Python files to compress")
    
    
    master_key = key or generate_key()
    
    results = []
    for file_path in python_files:
        output_file, file_key = compress_file(file_path, key=master_key)
        if output_file:
            results.append((file_path, output_file, file_key))
    
    
    key_file = os.path.join(directory_path, 'encryption_key.txt')
    with open(key_file, 'w') as f:
        f.write(f"Master encryption key: {master_key.decode()}\n")
        f.write("Keep this key safe - you'll need it to decrypt the files!\n")
    
    print(f"\n✓ Compressed {len(results)} files successfully")
    print(f"✓ Encryption key saved to: {key_file}")

def test_compressed_file(compressed_file):
    """
    Test if a compressed file can be executed
    """
    try:
        with open(compressed_file, 'r') as f:
            code = f.read()
        
        
        exec(code)
        print(f"✓ {compressed_file} executed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error executing {compressed_file}: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Compress single file: python fernet_compress.py <file_path>")
        print("  Compress directory:   python fernet_compress.py <directory_path>")
        print("  Test compressed file: python fernet_compress.py --test <compressed_file>")
        sys.exit(1)
    
    if sys.argv[1] == "--test" and len(sys.argv) == 3:
        test_compressed_file(sys.argv[2])
    elif os.path.isfile(sys.argv[1]):
        compress_file(sys.argv[1])
    elif os.path.isdir(sys.argv[1]):
        compress_directory(sys.argv[1])
    else:
        print(f"Error: {sys.argv[1]} is not a valid file or directory")