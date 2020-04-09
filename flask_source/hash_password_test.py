# encoding:UTF-8
from werkzeug.security import *

hash_password = generate_password_hash("This is password")
print(hash_password)
test_hash = "pbkdf2:sha256:150000$qoK7k8Ld$2829d791e5f6c7b7335a74eda7b05627b0493c79ad1334475743763f40dcee6a"
print(check_password_hash(test_hash, "This is password"))
