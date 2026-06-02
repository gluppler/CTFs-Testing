# Misc / General Quick Reference

```bash
# Encoding
echo 'base64string' | base64 -d
echo 'hexstring' | xxd -r -p
echo 'binary' | perl -lpe '$_=pack"B*",$_'

# Misc analysis
file unknown.file
binwalk -Me unknown.file

# Python jail escape
__import__('os').system('cat flag*')

# QR decode
zbarimg qr.png

# Audio
sox audio.wav -n spectrogram
```
