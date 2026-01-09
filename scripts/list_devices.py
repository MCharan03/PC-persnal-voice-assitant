import sounddevice as sd
print(sd.query_devices())
print("\nDefault Input Device:")
print(sd.query_devices(kind='input'))
